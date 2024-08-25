def calculate_task_score(importance: int, effort: int) -> int:
    """
    Calculates the score of a task based on its importance and effort.

    Args:
        importance (int): The importance of the task (between 1 and 4).
        effort (int): The effort required for the task (between 1 and 4).

    Returns:
        int: The calculated task score.

    Raises:
        ValueError: If importance or effort is not between 1 and 4.
    """
    if not (1 <= importance <= 4) or not (1 <= effort <= 4):
        raise ValueError("Importance and effort should be between 1 and 4.")

    score = round(25 * (importance * (1 / effort)))
    return score
