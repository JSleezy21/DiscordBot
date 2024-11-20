import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def calculate(expression):
    """
    Evaluates a mathematical expression and returns the result.
    :param expression: String of the mathematical expression.
    :return: Result of the calculation.
    """
    try:
        logger.info(f"Calculating expression: {expression}")
        # Evaluate the mathematical expression securely
        result = eval(expression, {"__builtins__": None}, {})
        logger.info(f"Calculation result: {result}")
        return result
    except Exception as e:
        logger.error(f"Error in calculation: {e}")
        return "Error: Invalid mathematical expression."
