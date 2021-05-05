pydoc-markdown \
-m beanie.odm.operators.find.comparsion \
-m beanie.odm.operators.find.logical \
-m beanie.odm.operators.find.element \
-m beanie.odm.operators.find.evaluation \
-m beanie.odm.operators.find.geospatial \
-m beanie.odm.operators.find.array \
-m beanie.odm.operators.find.bitwise \
 > docs/api/operators/find.md

pydoc-markdown \
-m beanie.odm.operators.update.general \
-m beanie.odm.operators.update.array \
-m beanie.odm.operators.update.bitwise \
 > docs/api/operators/update.md

pydoc-markdown \
-m beanie.odm.queries.find \
-m beanie.odm.queries.update \
-m beanie.odm.queries.delete \
-m beanie.odm.queries.aggregation \
-m beanie.odm.queries.cursor \
 > docs/api/queries.md

pydoc-markdown \
-m beanie.odm.interfaces.update \
-m beanie.odm.interfaces.aggregate \
-m beanie.odm.interfaces.session \
 > docs/api/interfaces.md

pydoc-markdown \
-m beanie.odm.documents \
 > docs/api/document.md

 pydoc-markdown \
-m beanie.odm.fields \
 > docs/api/fields.md