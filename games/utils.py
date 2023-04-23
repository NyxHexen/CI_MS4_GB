

def sort_by(sort_value, *args):
    """
    Sorts the given arguments (querysets) based on `sort_value`.

    Args:
        sort_value (str): The value based on which the arguments will be sorted.
        *args: Any number of querysets that get passed in.

    Returns:
        A combined flat, sorted, list of the passed in args.

    Raises:
        None.
    """
    # Convert each argument to a list
    sorted_args = [list(arg) for arg in args]
    # Flatten the list of lists into a single list
    sorted_args = [item for sublist in sorted_args for item in sublist]
    # Sort the list based on the value of sort_value
    match sort_value:
        case "price_desc":
            sorted_args.sort(
                key=lambda x: x.final_price, reverse=True
                )
        case "price_asc":
            sorted_args.sort(
                key=lambda x: x.final_price
                )
        case "discount_desc":
            sorted_args.sort(
                key=lambda x: x.promo_percentage,
                reverse=True
                )
        case "title_asc":
            sorted_args.sort(
                key=lambda x: x.name
                )
        case "title_desc":
            sorted_args.sort(
                key=lambda x: x.name, reverse=True
                )
        case "date_desc":
            sorted_args.sort(
                key=lambda x: x.release_date
                )
        case "date_asc":
            sorted_args.sort(
                key=lambda x: x.release_date, reverse=True
                )
        case "rating_desc":
            sorted_args.sort(
                key=lambda x: x.ratingset.user_rating_calc(),
                reverse=True
                )
        case _:
            pass
    return sorted_args