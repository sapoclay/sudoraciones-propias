"""
Módulos del Sistema de Entrenamiento
Sistema modular organizado por pestañas
"""

from .base_trainer import BaseTrainer
from .training_plan import TrainingPlanModule
from .progress_calendar import ProgressModule
from .statistics import StatisticsModule
from .info import InfoModule

__all__ = [
    'BaseTrainer',
    'TrainingPlanModule', 
    'ProgressModule',
    'StatisticsModule',
    'InfoModule'
]
