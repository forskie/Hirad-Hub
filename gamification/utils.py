from .constants import LEVELS

def update_level_and_title(user):
    new_level = LEVELS[0][1]       
    new_title = LEVELS[0][2]
        

    for points, level, title in LEVELS:
        if user.score >= points:
            new_level = level
            new_title = title
        else:
            break   
    old_level, old_title = user.level, user.title
    user.level = new_level
    user.title = new_title
    user.save(update_fields=['level', 'title'])
    return old_level != new_level, new_level, new_title
        
def add_score(user, points: int):
    if not isinstance(points, int):
        raise ValueError("Points must be an integer.")
    if points <= 0:
        return
    user.score += points
    user.save(update_fields=['score'])
    return update_level_and_title(user)