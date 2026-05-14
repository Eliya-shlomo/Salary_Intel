class SalaryIntelError(Exception):
    """Base exception לכל שגיאות הפרויקט"""
    pass


class EmbeddingError(SalaryIntelError):
    """נכשל ביצירת embedding"""
    pass


class RetrievalError(SalaryIntelError):
    """נכשל בחיפוש במסד"""
    pass


class GenerationError(SalaryIntelError):
    """נכשל ביצירת תשובה"""
    pass


class DatabaseError(SalaryIntelError):
    """שגיאת מסד נתונים"""
    pass