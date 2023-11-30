def plan_parser(plan: str) -> list:
    """
    Splits the given plan from planner agent into multiple sub-plans using ``` as a delimiter.

    Parameters:
    plan (str): Plan string which may contain ``` delimiter to break it into sub-plans.

    Returns:
    list: A list of sub-plans. Returns an empty list if no ``` delimiter is found.
    """

    if '```' not in plan:
        raise ValueError("No ``` delimiter found in Planner Agent's plan please rerun the command.")

    # Split plan into sub-plans using ``` as a delimiter and remove the first element (reasoning step)
    plans = plan.split('```')[1]
    # remove brackets and split into list
    plans = plans.replace('\n','').replace('[','').replace(']','').replace('python','').split(',')
    plan_list = [plan.strip() for plan in plans]
    return plan_list






def print_color(string: str, color: str) -> None:
    """
    Prints a string on console in a given color.

    Parameters:
    string (str): The string to be printed on console
    color (str): The color code for the string to be printed in

    Returns:
    None
    """
    # Print string with the given color and reset console color to default afterwards
    print("\033["+color+"m"+string+"\033[0m")
