from typing import Dict, ForwardRef, Type, Union, Optional, List

from pydantic import BaseModel


class ForwardRefProxy:
    """
    A proxy class that acts as a placeholder for unresolved forward references.
    It defers the resolution until the class is actually needed.
    """
    
    def __init__(self, forward_ref: ForwardRef, registry: Type['DocsRegistry']):
        self.forward_ref = forward_ref
        self.registry = registry
        self._resolved_class: Optional[Type[BaseModel]] = None
    
    def resolve(self) -> Type[BaseModel]:
        """Resolve the forward reference to the actual class"""
        if self._resolved_class is None:
            class_name = self.forward_ref.__forward_arg__
            if class_name in self.registry._registry:
                self._resolved_class = self.registry._registry[class_name]
            else:
                raise ValueError(
                    f"Forward reference '{class_name}' could not be resolved. "
                    f"Make sure the class is properly imported and registered."
                )
        # At this point _resolved_class is guaranteed to be not None
        assert self._resolved_class is not None
        return self._resolved_class
    
    def __getattr__(self, name):
        """Delegate attribute access to the resolved class"""
        resolved = self.resolve()
        return getattr(resolved, name)
    
    def __call__(self, *args, **kwargs):
        """Allow the proxy to be called like the actual class"""
        return self.resolve()(*args, **kwargs)
    
    def __eq__(self, other):
        """Support equality comparison"""
        if isinstance(other, ForwardRefProxy):
            return self.resolve() == other.resolve()
        return self.resolve() == other
    
    def __hash__(self):
        """Support hashing"""
        return hash(self.resolve())
    
    def __repr__(self):
        """Provide useful representation"""
        try:
            resolved = self.resolve()
            return f"<ForwardRefProxy[{resolved.__name__}]>"
        except ValueError:
            return f"<ForwardRefProxy[{self.forward_ref.__forward_arg__}] (unresolved)>"


class DocsRegistry:
    _registry: Dict[str, Type[BaseModel]] = {}
    _pending_models: List[Type[BaseModel]] = []  # Models that need rebuilding

    @classmethod
    def register(cls, name: str, doc_type: Type[BaseModel]):
        cls._registry[name] = doc_type
        # Add to pending models for later rebuilding
        if doc_type not in cls._pending_models:
            cls._pending_models.append(doc_type)

    @classmethod
    def get(cls, name: str) -> Type[BaseModel]:
        return cls._registry[name]

    @classmethod
    def evaluate_fr(cls, forward_ref: Union[ForwardRef, Type[BaseModel]]):
        """
        Evaluate forward ref

        :param forward_ref: ForwardRef - forward ref to evaluate
        :return: Type[BaseModel] - class of the forward ref
        """
        if isinstance(forward_ref, ForwardRef):
            class_name = forward_ref.__forward_arg__
            if class_name in cls._registry:
                return cls._registry[class_name]
            else:
                # Return a proxy that will resolve the forward reference lazily
                return ForwardRefProxy(forward_ref, cls)
        else:
            return forward_ref

    @classmethod
    def rebuild_models(cls):
        """
        Rebuild all pending models to resolve forward references.
        This is called after all models are registered.
        """
        from beanie.odm.utils.pydantic import IS_PYDANTIC_V2
        
        if IS_PYDANTIC_V2:
            # For Pydantic v2, inject all registered classes into the global namespace
            # of each model's module before rebuilding
            for model in cls._pending_models:
                module = model.__module__
                if hasattr(model, '__module__'):
                    import sys
                    model_module = sys.modules.get(module)
                    if model_module:
                        # Inject all registered classes into the model's module namespace
                        for name, registered_class in cls._registry.items():
                            if not hasattr(model_module, name):
                                setattr(model_module, name, registered_class)
                
                try:
                    model.model_rebuild()
                except Exception:
                    # Continue with other models if one fails
                    continue
        else:
            # For Pydantic v1, use update_forward_refs
            for model in cls._pending_models:
                try:
                    if hasattr(model, 'update_forward_refs'):
                        # Pass the registry as the global namespace
                        model.update_forward_refs(**cls._registry)
                except Exception:
                    continue
        
        # After rebuilding models, resolve ForwardRefProxy objects in LinkInfo
        cls._resolve_link_info_forward_refs()
        
        # Clear pending models after rebuild
        cls._pending_models.clear()

    @classmethod
    def _resolve_link_info_forward_refs(cls):
        """
        Resolve ForwardRefProxy objects in LinkInfo after all models are rebuilt.
        This ensures that LinkInfo.document_class points to actual classes, not proxies.
        """
        for model in cls._pending_models:
            if hasattr(model, '_link_fields') and getattr(model, '_link_fields', None):
                link_fields = getattr(model, '_link_fields')
                for field_name, link_info in link_fields.items():
                    if isinstance(link_info.document_class, ForwardRefProxy):
                        try:
                            # Replace the proxy with the resolved class
                            link_info.document_class = link_info.document_class.resolve()
                        except ValueError:
                            # If resolution fails, keep the proxy (it will raise an error when used)
                            pass

    @classmethod
    def clear(cls):
        """Clear the registry"""
        cls._registry.clear()
        cls._pending_models.clear()
