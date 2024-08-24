import adapters
from adapters import AdapterConfig, AutoAdapterModel, BnConfig
from transformers import AutoModel

# model = AutoModel.from_pretrained("google-bert/bert-base-uncased", num_labels=5)
# adapters.init(model)

model = AutoAdapterModel.from_pretrained("google-bert/bert-base-uncased", num_labels=5)

model.config.bad_connfig = 1

config = BnConfig(
    mh_adapter=True, output_adapter=True, reduction_factor=16, non_linearity="relu"
)
model.add_adapter("bottleneck_adapter", config=config)

model.train_adapter("bottleneck_adapter")
