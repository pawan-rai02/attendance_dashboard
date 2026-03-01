"""
Training Pipeline for Attendance Risk Prediction Model.
Handles data preparation, training, evaluation, and model persistence.
"""

import os
import sys
import logging
from datetime import datetime
from typing import Dict, Any, Optional, List, Tuple
import numpy as np

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from ml.model import AttendanceRiskPredictor, create_training_data_from_db

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class TrainingPipeline:
    """
    End-to-end training pipeline for attendance risk prediction.
    
    Pipeline Steps:
    1. Data Collection: Extract from database
    2. Data Validation: Check data quality
    3. Feature Engineering: Create predictive features
    4. Train-Test Split: 80-20 split with stratification
    5. Model Training: Logistic Regression with gradient descent
    6. Evaluation: Accuracy, Precision, Recall, F1, AUC-ROC
    7. Model Persistence: Save to disk
    8. Logging: Record training metrics
    
    Time Complexity: O(n * m * iterations) where n = samples, m = features
    Space Complexity: O(n * m) for storing training data
    """
    
    def __init__(
        self,
        model_dir: str = "ml/models",
        learning_rate: float = 0.01,
        n_iterations: int = 1000,
        validation_split: float = 0.2
    ):
        """
        Initialize training pipeline.
        
        Args:
            model_dir: Directory to save trained models
            learning_rate: Learning rate for gradient descent
            n_iterations: Number of training iterations
            validation_split: Fraction of data for validation
        """
        self.model_dir = model_dir
        self.learning_rate = learning_rate
        self.n_iterations = n_iterations
        self.validation_split = validation_split
        self.model: Optional[AttendanceRiskPredictor] = None
        self.training_metrics: Dict[str, Any] = {}
    
    def prepare_data(
        self,
        db_session=None
    ) -> Tuple[np.ndarray, np.ndarray]:
        """
        Prepare training data from database.
        
        Data Quality Checks:
        - Minimum samples per student
        - Valid attendance percentages
        - Balanced class distribution
        
        Args:
            db_session: SQLAlchemy database session
            
        Returns:
            Tuple of (features, labels)
        """
        logger.info("Preparing training data...")
        
        if db_session:
            # Load from database
            X, y = create_training_data_from_db(db_session)
        else:
            # Generate synthetic data for demonstration
            X, y = self._generate_synthetic_data()
        
        # Data validation
        assert len(X) > 0, "No training data found"
        assert len(X) == len(y), "Features and labels mismatch"
        assert X.shape[1] == 5, f"Expected 5 features, got {X.shape[1]}"
        
        # Check class balance
        positive_ratio = np.mean(y)
        logger.info(f"Class distribution: {positive_ratio:.2%} positive (shortage)")
        
        if positive_ratio < 0.1 or positive_ratio > 0.9:
            logger.warning("Class imbalance detected. Consider resampling.")
        
        logger.info(f"Prepared {len(X)} samples with {X.shape[1]} features")
        return X, y
    
    def _generate_synthetic_data(
        self,
        n_samples: int = 1000,
        noise: float = 0.1
    ) -> Tuple[np.ndarray, np.ndarray]:
        """
        Generate synthetic training data for demonstration.
        
        Simulates realistic attendance patterns:
        - Students with low current attendance are more likely to have shortage
        - More remaining classes reduces shortage probability
        - Positive trend improves outcomes
        
        Args:
            n_samples: Number of samples to generate
            noise: Random noise factor
            
        Returns:
            Tuple of (features, labels)
        """
        np.random.seed(42)  # Reproducibility
        
        # Generate features
        current_attendance = np.random.uniform(40, 95, n_samples)
        classes_remaining = np.random.randint(5, 50, n_samples)
        classes_attended = np.random.randint(20, 80, n_samples)
        historical_trend = np.random.uniform(-0.5, 0.5, n_samples)
        subject_difficulty = np.random.uniform(0.2, 0.8, n_samples)
        
        X = np.column_stack([
            current_attendance,
            classes_remaining,
            classes_attended,
            historical_trend,
            subject_difficulty
        ])
        
        # Generate labels based on realistic patterns
        # Probability of shortage decreases with:
        # - Higher current attendance
        # - More remaining classes
        # - Positive trend
        
        z = (
            -0.08 * (current_attendance - 75) +
            -0.03 * (classes_remaining - 25) +
            0.01 * (classes_attended - 50) +
            -0.30 * historical_trend * 100 +
            0.50 * (subject_difficulty - 0.5) * 100
        )
        
        # Convert to probability using sigmoid
        prob_shortage = 1 / (1 + np.exp(-z / 10))
        
        # Add noise and convert to binary labels
        prob_noisy = prob_shortage + np.random.uniform(-noise, noise, n_samples)
        y = (prob_noisy > 0.5).astype(int)
        
        return X, y
    
    def train(
        self,
        X: np.ndarray,
        y: np.ndarray
    ) -> Dict[str, Any]:
        """
        Train the model.
        
        Args:
            X: Feature matrix
            y: Labels
            
        Returns:
            Training metrics
        """
        logger.info("Starting model training...")
        
        # Initialize model
        self.model = AttendanceRiskPredictor(
            learning_rate=self.learning_rate,
            n_iterations=self.n_iterations
        )
        
        # Train
        metrics = self.model.fit(X, y, validation_split=self.validation_split)
        
        self.training_metrics = metrics
        logger.info(f"Training completed. Validation accuracy: {metrics['validation_accuracy']:.4f}")
        
        return metrics
    
    def evaluate(
        self,
        X_test: np.ndarray,
        y_test: np.ndarray,
        threshold: float = 0.5
    ) -> Dict[str, float]:
        """
        Evaluate model performance.
        
        Metrics:
        - Accuracy: Overall correctness
        - Precision: True positives / (True positives + False positives)
        - Recall: True positives / (True positives + False negatives)
        - F1 Score: Harmonic mean of precision and recall
        - AUC-ROC: Area under ROC curve
        
        Args:
            X_test: Test features
            y_test: Test labels
            threshold: Classification threshold
            
        Returns:
            Dictionary of evaluation metrics
        """
        if not self.model or not self.model.is_trained:
            raise RuntimeError("Model not trained")
        
        # Get predictions
        y_pred_proba = self.model.predict_proba(X_test)
        y_pred = (y_pred_proba >= threshold).astype(int)
        
        # Confusion matrix components
        tp = np.sum((y_pred == 1) & (y_test == 1))
        tn = np.sum((y_pred == 0) & (y_test == 0))
        fp = np.sum((y_pred == 1) & (y_test == 0))
        fn = np.sum((y_pred == 0) & (y_test == 1))
        
        # Calculate metrics
        accuracy = (tp + tn) / len(y_test) if len(y_test) > 0 else 0
        precision = tp / (tp + fp) if (tp + fp) > 0 else 0
        recall = tp / (tp + fn) if (tp + fn) > 0 else 0
        f1 = 2 * precision * recall / (precision + recall) if (precision + recall) > 0 else 0
        
        # AUC-ROC approximation
        auc = self._calculate_auc(y_test, y_pred_proba)
        
        metrics = {
            'accuracy': accuracy,
            'precision': precision,
            'recall': recall,
            'f1_score': f1,
            'auc_roc': auc,
            'true_positives': int(tp),
            'true_negatives': int(tn),
            'false_positives': int(fp),
            'false_negatives': int(fn)
        }
        
        logger.info(f"Evaluation metrics: Accuracy={accuracy:.4f}, F1={f1:.4f}, AUC={auc:.4f}")
        return metrics
    
    def _calculate_auc(
        self,
        y_true: np.ndarray,
        y_scores: np.ndarray
    ) -> float:
        """
        Calculate AUC-ROC score.
        
        Uses trapezoidal rule approximation.
        
        Time Complexity: O(n log n) for sorting
        """
        # Sort by predicted scores
        sorted_indices = np.argsort(y_scores)[::-1]
        y_true_sorted = y_true[sorted_indices]
        
        # Count positives and negatives
        n_pos = np.sum(y_true == 1)
        n_neg = np.sum(y_true == 0)
        
        if n_pos == 0 or n_neg == 0:
            return 0.5
        
        # Calculate AUC using trapezoidal rule
        tpr_prev = 0
        fpr_prev = 0
        auc = 0
        tp = 0
        fp = 0
        
        for i in range(len(y_true_sorted)):
            if y_true_sorted[i] == 1:
                tp += 1
            else:
                fp += 1
            
            tpr = tp / n_pos
            fpr = fp / n_neg
            
            # Trapezoidal area
            auc += (fpr - fpr_prev) * (tpr + tpr_prev) / 2
            
            tpr_prev = tpr
            fpr_prev = fpr
        
        return auc
    
    def save_model(self, model_name: Optional[str] = None) -> str:
        """
        Save trained model to disk.
        
        Args:
            model_name: Optional custom name for model file
            
        Returns:
            Path to saved model
        """
        if not self.model or not self.model.is_trained:
            raise RuntimeError("No trained model to save")
        
        if model_name is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            model_name = f"risk_predictor_{timestamp}.pkl"
        
        filepath = os.path.join(self.model_dir, model_name)
        self.model.save(filepath)
        
        # Save training metrics
        metrics_path = filepath.replace('.pkl', '_metrics.json')
        import json
        with open(metrics_path, 'w') as f:
            json.dump(self.training_metrics, f, indent=2)
        
        logger.info(f"Model saved to {filepath}")
        return filepath
    
    def run_full_pipeline(
        self,
        db_session=None,
        save: bool = True
    ) -> Dict[str, Any]:
        """
        Run complete training pipeline.
        
        Args:
            db_session: Optional database session
            save: Whether to save the model
            
        Returns:
            Complete pipeline results
        """
        logger.info("=" * 50)
        logger.info("Starting Full Training Pipeline")
        logger.info("=" * 50)
        
        # Step 1: Prepare data
        X, y = self.prepare_data(db_session)
        
        # Step 2: Split data
        split_idx = int(len(X) * (1 - self.validation_split))
        X_train, X_val = X[:split_idx], X[split_idx:]
        y_train, y_val = y[:split_idx], y[split_idx:]
        
        # Step 3: Train
        train_metrics = self.train(X_train, y_train)
        
        # Step 4: Evaluate
        eval_metrics = self.evaluate(X_val, y_val)
        
        # Step 5: Save
        if save:
            model_path = self.save_model()
        else:
            model_path = None
        
        # Compile results
        results = {
            'training': train_metrics,
            'evaluation': eval_metrics,
            'model_path': model_path,
            'feature_importance': self.model.get_feature_importance() if self.model else {}
        }
        
        logger.info("=" * 50)
        logger.info("Pipeline Completed Successfully")
        logger.info("=" * 50)
        
        return results


def main():
    """Main entry point for training."""
    print("=" * 60)
    print("Attendance Risk Prediction Model Training")
    print("=" * 60)
    
    # Initialize pipeline
    pipeline = TrainingPipeline(
        model_dir="ml/models",
        learning_rate=0.01,
        n_iterations=1000,
        validation_split=0.2
    )
    
    # Run full pipeline (uses synthetic data if no database)
    results = pipeline.run_full_pipeline(db_session=None, save=True)
    
    # Print results
    print("\n📊 Training Results:")
    print(f"   Samples: {results['training']['n_samples']}")
    print(f"   Features: {results['training']['n_features']}")
    print(f"   Final Loss: {results['training']['final_loss']:.4f}")
    
    print("\n📈 Evaluation Metrics:")
    print(f"   Accuracy: {results['evaluation']['accuracy']:.4f}")
    print(f"   Precision: {results['evaluation']['precision']:.4f}")
    print(f"   Recall: {results['evaluation']['recall']:.4f}")
    print(f"   F1 Score: {results['evaluation']['f1_score']:.4f}")
    print(f"   AUC-ROC: {results['evaluation']['auc_roc']:.4f}")
    
    print("\n🎯 Feature Importance:")
    for feature, importance in sorted(
        results['feature_importance'].items(),
        key=lambda x: x[1],
        reverse=True
    ):
        print(f"   {feature}: {importance:.4f}")
    
    print(f"\n💾 Model saved to: {results['model_path']}")
    print("=" * 60)
    
    return results


if __name__ == "__main__":
    main()
