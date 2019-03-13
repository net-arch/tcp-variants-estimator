# tcp-variants-estimator
## data flow
```
                          + - train
dump - estimate - extract +
                          + - test
```
## setup
```
cd tcp-variants-estimator
mkdir -p data/dump data/estimate data/estimate_for_graph data/train data/test data/result data/img/estiamte data/img/result
python3 -m venv venv
source ./venv/bin/activate
pip install -r requirements.txt
``
