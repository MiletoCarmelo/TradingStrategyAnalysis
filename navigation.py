from taipy.gui import navigate

def on_navigate(state, page):
    navigate(state, page)
    return page  # Add this line to return the page name

layout = """
<|layout|
<|part|class_name=left-navbar|
<|Home|button|class_name=nav-item|on_action=on_navigate|partial=True|page=home|>
<|Dashboard|button|class_name=nav-item|on_action=on_navigate|partial=True|page=dashboard|>
<|Analysis|button|class_name=nav-item|on_action=on_navigate|partial=True|page=analysis|>
<|Settings|button|class_name=nav-item|on_action=on_navigate|partial=True|page=settings|>
|>

<|part|class_name=main-content|
<|content|>
|>
|>
"""