#pydoc-markdown -I beanie/odm/operators --render-toc > docs/api/operators.md
pydoc-markdown \
-m beanie.odm.operators.find.comparsion \
-m beanie.odm.operators.find.logical \
-m beanie.odm.operators.find.element \
-m beanie.odm.operators.find.evaluation \
-m beanie.odm.operators.find.geospatial \
-m beanie.odm.operators.find.array \
-m beanie.odm.operators.find.bitwise \
--render-toc > docs/api/operators.md