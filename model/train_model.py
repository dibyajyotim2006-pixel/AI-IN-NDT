import os
import joblib
import numpy as np
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.neural_network import MLPRegressor
from sklearn.preprocessing import StandardScaler
from sklearn.compose import TransformedTargetRegressor
from sklearn.metrics import mean_squared_error, mean_absolute_error, r2_score

def engineer_features(df):
    """
    Generate the 6 input features documented in the IDP architecture:
    1. Age
    2. Rebound Index
    3. UPV
    4. UPV / Age
    5. Rebound Index / Age
    6. UPV * Rebound Index
    """
    X = pd.DataFrame()
    X['Age'] = df['Age'].astype(float)
    X['Rebound_Index'] = df['Rebound_Index'].astype(float)
    X['UPV'] = df['UPV'].astype(float)
    
    # Feature 4: UPV / Age
    X['UPV_over_Age'] = X['UPV'] / X['Age']
    
    # Feature 5: Rebound Index / Age
    X['Rebound_over_Age'] = X['Rebound_Index'] / X['Age']
    
    # Feature 6: UPV * Rebound Index
    X['UPV_x_Rebound'] = X['UPV'] * X['Rebound_Index']
    
    return X

def train_and_save_model(data_path="data/concrete_samples.csv", model_output_path="model/trained_model.pkl"):
    print("Loading concrete dataset from:", data_path)
    df = pd.read_csv(data_path)
    
    X = engineer_features(df)
    y = df['Actual_Strength'].astype(float)
    
    # Split into Train (80%) and Test (20%)
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.20, random_state=42
    )
    
    print(f"Dataset split: Total={len(df)}, Train={len(X_train)}, Test={len(X_test)}")
    
    # ANN Architecture specified in Kiran IDP:
    # 6 Input neurons, 6 Hidden neurons, Sigmoid activation, Linear output, Supervised backpropagation
    # hidden_layer_sizes=(6,)
    # activation='logistic' (Sigmoid)
    # solver='lbfgs' (Supervised quasi-Newton backpropagation optimization)
    base_mlp = MLPRegressor(
        hidden_layer_sizes=(6,),
        activation='logistic',   # Sigmoid hidden activation
        solver='lbfgs',          # Backpropagation optimizer
        max_iter=3000,
        random_state=42,
        tol=1e-5
    )
    
    scaler_X = StandardScaler()
    scaler_y = StandardScaler()
    
    # TransformedTargetRegressor applies linear standardization to output y for stable convergence
    pipeline = TransformedTargetRegressor(
        regressor=base_mlp,
        transformer=scaler_y
    )
    
    X_train_scaled = scaler_X.fit_transform(X_train)
    X_test_scaled = scaler_X.transform(X_test)
    
    print("Training Artificial Neural Network (6-6-1 architecture, Sigmoid hidden activation)...")
    pipeline.fit(X_train_scaled, y_train)
    
    # Predictions
    y_train_pred = pipeline.predict(X_train_scaled)
    y_test_pred = pipeline.predict(X_test_scaled)
    
    # Overall predictions across full dataset
    X_all_scaled = scaler_X.transform(X)
    y_all_pred = pipeline.predict(X_all_scaled)
    
    # Metrics
    train_mse = mean_squared_error(y_train, y_train_pred)
    test_mse = mean_squared_error(y_test, y_test_pred)
    test_rmse = np.sqrt(test_mse)
    test_mae = mean_absolute_error(y_test, y_test_pred)
    test_r2 = r2_score(y_test, y_test_pred)
    test_r = float(np.corrcoef(y_test, y_test_pred)[0, 1])
    
    all_r2 = r2_score(y, y_all_pred)
    all_r = float(np.corrcoef(y, y_all_pred)[0, 1])
    all_mse = mean_squared_error(y, y_all_pred)
    all_mae = mean_absolute_error(y, y_all_pred)
    all_rmse = np.sqrt(all_mse)
    
    metrics = {
        "train_mse": float(round(train_mse, 5)),
        "test_mse": float(round(test_mse, 5)),
        "test_rmse": float(round(test_rmse, 5)),
        "test_mae": float(round(test_mae, 5)),
        "test_r2": float(round(test_r2, 5)),
        "test_r": float(round(test_r, 5)),
        "overall_r": float(round(all_r, 5)),
        "overall_r2": float(round(all_r2, 5)),
        "overall_mse": float(round(all_mse, 5)),
        "overall_rmse": float(round(all_rmse, 5)),
        "overall_mae": float(round(all_mae, 5)),
        "feature_names": list(X.columns),
        "architecture": {
            "input_features": 6,
            "hidden_layers": 1,
            "hidden_neurons": 6,
            "hidden_activation": "Sigmoid (Logistic)",
            "output_activation": "Linear Identity",
            "optimizer": "L-BFGS Supervised Backpropagation",
            "weights_shape": "(6, 6) + (6, 1)"
        }
    }
    
    print("\n================ MODEL EVALUATION METRICS ================")
    print(f"Test Correlation (R):       {test_r:.5f} (Report target: 0.99486)")
    print(f"Test Coefficient (R²):     {test_r2:.5f}")
    print(f"Test Mean Squared Error:   {test_mse:.5f}")
    print(f"Test Root Mean Sq Error:   {test_rmse:.5f} MPa")
    print(f"Test Mean Absolute Error:  {test_mae:.5f} MPa")
    print(f"Full Dataset Correlation R:{all_r:.5f}")
    print(f"Full Dataset MSE:          {all_mse:.5f}")
    print("==========================================================")
    
    # Save predicted column to concrete_samples_predicted.csv for instant analytics
    df_eval = df.copy()
    df_eval['Predicted_Strength'] = np.round(y_all_pred, 2)
    df_eval['Prediction_Error'] = np.round(df_eval['Predicted_Strength'] - df_eval['Actual_Strength'], 2)
    df_eval.to_csv("data/concrete_samples_evaluated.csv", index=False)
    
    os.makedirs(os.path.dirname(model_output_path), exist_ok=True)
    bundle = {
        "pipeline": pipeline,
        "scaler_X": scaler_X,
        "features": list(X.columns),
        "metrics": metrics
    }
    
    joblib.dump(bundle, model_output_path)
    print(f"Trained model bundle successfully saved to {model_output_path}")
    return bundle

if __name__ == "__main__":
    train_and_save_model()
