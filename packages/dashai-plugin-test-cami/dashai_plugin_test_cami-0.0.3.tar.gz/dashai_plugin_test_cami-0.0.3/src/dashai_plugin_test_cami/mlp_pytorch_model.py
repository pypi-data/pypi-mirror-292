from DashAI.back.core.schema_fields import BaseSchema, schema_field, int_field, list_field, float_field
from DashAI.back.models.base_model import BaseModel
from DashAI.back.config_object import ConfigObject

import torch.utils.data
import datasets
from torchvision import transforms
import torch
import torch.nn as nn
import torch.optim as optim
from torch.utils.data import DataLoader, Dataset


# Multi Layer Perceptron class
class MLP(nn.Module):
    def __init__(self, input_dim, output_dim, hidden_dims):
        super().__init__()
        self.hidden_layers = nn.ModuleList()
        previous_dim = input_dim

        for hidden_dim in hidden_dims:
            self.hidden_layers.append(nn.Linear(previous_dim, hidden_dim))
            previous_dim = hidden_dim

        self.output_layer = nn.Linear(previous_dim, output_dim)
        self.relu = nn.ReLU()

    def forward(self, input: torch.Tensor):
        batch_size = input.shape[0]
        x = input.view(batch_size, -1)

        for layer in self.hidden_layers:
            x = self.relu(layer(x))

        x = self.output_layer(x)
        return x

# Auxiliary functions
def fit_model(
    model: nn.Module,
    train_loader: DataLoader,
    epochs: int,
    criterion: nn.Module,
    optimizer: optim.Optimizer,
    device: torch.device
):
    model.train()
    for epoch in range(epochs):
        for images, labels in train_loader:
            images, labels = images.to(device), labels.to(device)
            optimizer.zero_grad()
            outputs = model(images)
            loss = criterion(outputs, labels)
            loss.backward()
            optimizer.step()
        print(f"Epoch {epoch+1}/{epochs}, Loss: {loss.item()}")
    return model

def predict(
    model: nn.Module,
    dataloader: DataLoader,
    device: torch.device,
):
    model.eval()
    probs_predicted = []
    with torch.no_grad():
        for images in dataloader:
            images = images.to(device)
            output_probs: torch.Tensor = model(images)
            probs_predicted += output_probs.tolist()
    return probs_predicted


# This class helps to transform data to pytorch-compatible format
class TransformedImageDataset(torch.utils.data.Dataset):
    def __init__(self, dataset: datasets.Dataset):
        self.dataset = dataset
        self.transforms = transforms.Compose([
                transforms.Resize((30, 30)),
                transforms.ToTensor(),
            ])

        column_names = list(self.dataset.features.keys())
        self.image_col_name = column_names[0]
        self.tensor_shape = self.transforms(self.dataset[0][self.image_col_name]).shape
        self.input_dim = (self.tensor_shape[0] *
                          self.tensor_shape[1] *
                          self.tensor_shape[2])
        if len(column_names) > 1:
            self.label_col_name = column_names[1]
            self.output_dim = len(set(self.dataset[self.label_col_name]))
        else:
            self.label_col_name = None

    def __len__(self):
        return len(self.dataset)

    def __getitem__(self, idx):
        image = self.dataset[idx][self.image_col_name]
        image = self.transforms(image)
        if self.label_col_name is None:
            return image
        label = self.dataset[idx][self.label_col_name]
        return image, label


class MLPImageClassifierSchema(BaseSchema):
    epochs: schema_field(  # Change example_param_name
        int_field(ge=1), # Choose between different types_fields e.g. int_field, string_field, etc
        placeholder=3, # Placeholde to display in UI
        description=(
            "Number of epochs to train the model"
        ),
    )  # type: ignore

    learning_rate: schema_field(  # Change example_param_name
        float_field(gt=0), # Choose between different types_fields e.g. int_field, string_field, etc
        placeholder=0.1, # Placeholde to display in UI
        description=(
            "Learning rate"
        ),
    )  # type: ignore

    hidden_dims: schema_field(  # Change example_param_name
        list_field(item_type=int_field(gt=0)), # Choose between different types_fields e.g. int_field, string_field, etc
        placeholder=0.1, # Placeholde to display in UI
        description=(
            "hidden dimentions description"
        ),
    )  # type: ignore


class MLPImageClassifier(BaseModel, ConfigObject):

    SCHEMA = MLPImageClassifierSchema
    COMPATIBLE_COMPONENTS =["ImageClassificationTask"]

    def __init__(self, epochs, learning_rate, hidden_dims, **kwargs):
        super().__init__(**kwargs)
        self.epochs = epochs
        self.hidden_dims = hidden_dims
        self.learning_rate = learning_rate
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        self.model = None

    def fit(self, x_train: datasets.Dataset, y_train: datasets.Dataset):
        # Adapt adn transform x_train and y_train datasets to Pytorch Dataset
        dataset = datasets.Dataset.from_dict(
            {
                "image": x_train["image"],
                "label": y_train["label"],
            }
        )
        image_dataset = TransformedImageDataset(dataset)
        train_loader = DataLoader(image_dataset, batch_size=32, shuffle=True)

        # Set model
        self.model = MLP(
            image_dataset.input_dim,
            image_dataset.output_dim,
            self.hidden_dims
        ).to(self.device)
        self.criteria = nn.CrossEntropyLoss()
        self.optimizer = optim.Adam(self.model.parameters(), lr=self.learning_rate)
        self.model = fit_model(
            self.model,
            train_loader,
            self.epochs,
            self.criteria,
            self.optimizer,
            self.device,
        )

    def predict(self, x_pred: datasets.Dataset):
        image_dataset = TransformedImageDataset(x_pred)
        test_loader = DataLoader(image_dataset, batch_size=32, shuffle=False)
        predicted = predict(self.model, test_loader, self.device)
        return predicted

    def predict_one_image(self, image):
        self.model.eval()
        image = image.to(self.device)
        output = self.model(image)
        _, predicted = torch.max(output, 1)
        return predicted

    def save(self, filename: str) -> None:
        """Save the model in the specified path."""
        torch.save(self.model, filename)

    @staticmethod
    def load(filename: str) -> None:
        """Load the model of the specified path."""
        model = torch.load(filename)
        return model