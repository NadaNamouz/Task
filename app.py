import flet as ft
from datetime import date, datetime

# ---------- COLORS ----------
LIGHT = {
    "bg": "#F4F6FA",       
    "card": "#FFFFFF",     
    "text": "#202939",     
    "subtext": "#687386",  
    "chip": "#E8ECF4",     
}
DARK = {
    "bg": "#12141C",
    "card": "#1E2230",
    "text": "#F1F3F9",
    "subtext": "#9AA3B5",
    "chip": "#2A3045",
}

CATEGORIES = {
    "Work": "#4059AD",
    "Personal": "#2BAE66",
    "Study": "#F39C12",
    "Health": "#E5546B",
}

RED = "#E5484D"      # overdue
ORANGE = "#F5A524"   # due today / tomorrow
GREEN = "#2BAE66"    # plenty of time


def main(page: ft.Page):
    page.title = "Task Planner"
    page.padding = 30
    page.window.width = 700
    page.window.height = 800
    page.scroll = ft.ScrollMode.AUTO

    tasks = []

    state = {
        "dark": False,          
        "filter": "All",         # which category are we viewing?
        "new_category": "Work",  # category for the next task we add
        "due": "",               
    }

    def colors():
        return DARK if state["dark"] else LIGHT

    task_input = ft.TextField(
        hint_text="What do you need to do?",
        expand=True,
        border_radius=12,
    )

    # calendar
    date_button = ft.Button("Pick date", icon=ft.Icons.CALENDAR_MONTH)

    # Small "x" next to the date button to remove the chosen date.
    clear_date_button = ft.IconButton(
        icon=ft.Icons.CLOSE,
        tooltip="Remove date",
        visible=False,  
    )

    # The calendar pop-up.
    date_picker = ft.DatePicker()

    title_text = ft.Text("My Tasks", size=30, weight=ft.FontWeight.BOLD)
    subtitle_text = ft.Text("A little progress every day.", size=15)
    task_count = ft.Text("0 tasks remaining")
    reminder_text = ft.Text("", weight=ft.FontWeight.W_600)  # overdue / due today banner
    label_text = ft.Text("YOUR TASKS", size=12, weight=ft.FontWeight.BOLD)
    add_label = ft.Text("Add to:", size=13)

    filter_row = ft.Row(spacing=8, wrap=True)    # filter buttons
    category_row = ft.Row(spacing=8, wrap=True)  
    task_list = ft.Column(spacing=10)

    theme_button = ft.IconButton(icon=ft.Icons.DARK_MODE, tooltip="Dark / light mode")

    # ---------- Helpers ----------
    def make_chip(label, color, selected, on_click):
        return ft.Container(
            content=ft.Text(
                label,
                size=13,
                weight=ft.FontWeight.W_600,
                color="#FFFFFF" if selected else color,
            ),
            bgcolor=color if selected else colors()["chip"],
            padding=ft.Padding(left=14, top=6, right=14, bottom=6),
            border_radius=20,
            on_click=on_click,
        )

    def update_date_button():
        # Shows the chosen date on the button (or "Pick date" if none is chosen).
        p = colors()
        if state["due"]:
            picked = datetime.strptime(state["due"], "%Y-%m-%d")
            date_button.content = picked.strftime("%d %b %Y")
        else:
            date_button.content = "Pick date"

        date_button.bgcolor = p["bg"]
        date_button.color = p["text"]
        clear_date_button.icon_color = p["subtext"]
        clear_date_button.visible = bool(state["due"]) 

    def due_info(task):
        p = colors()
        if not task["due"]:
            return "", p["subtext"]

        due_date = datetime.strptime(task["due"], "%Y-%m-%d").date()
        days_left = (due_date - date.today()).days

        if task["done"]:
            return f"Due {task['due']}", p["subtext"]
        if days_left < 0:
            return f"Overdue by {-days_left} day(s)", RED
        if days_left == 0:
            return "Due today", ORANGE
        if days_left == 1:
            return "Due tomorrow", ORANGE
        return f"Due in {days_left} days ({task['due']})", GREEN

    def update_summary():
        remaining = 0
        overdue = 0
        due_today = 0

        for task in tasks:
            if task["done"]:
                continue
            remaining += 1
            if task["due"]:
                due_date = datetime.strptime(task["due"], "%Y-%m-%d").date()
                if due_date < date.today():
                    overdue += 1
                elif due_date == date.today():
                    due_today += 1

        task_count.value = f"{remaining} task(s) remaining"

        if overdue > 0:
            reminder_text.value = f"⚠ {overdue} overdue, {due_today} due today"
            reminder_text.color = RED
        elif due_today > 0:
            reminder_text.value = f"⏰ {due_today} task(s) due today"
            reminder_text.color = ORANGE
        else:
            reminder_text.value = "✓ Nothing urgent"
            reminder_text.color = GREEN

    # ---------- Main Screen ----------
    def render_filters():
        # Row of buttons: All + one per category.
        filter_row.controls.clear()
        filter_row.controls.append(
            make_chip("All", "#6C7A96", state["filter"] == "All",
                      lambda e: set_filter("All"))
        )
        for name, color in CATEGORIES.items():
            filter_row.controls.append(
                make_chip(name, color, state["filter"] == name,
                          lambda e, n=name: set_filter(n))
            )

    def render_category_picker():
        category_row.controls.clear()
        for name, color in CATEGORIES.items():
            category_row.controls.append(
                make_chip(name, color, state["new_category"] == name,
                          lambda e, n=name: set_new_category(n))
            )

    def render_tasks():
        p = colors()
        task_list.controls.clear()

        visible = []
        for task in tasks:
            if state["filter"] == "All" or task["category"] == state["filter"]:
                visible.append(task)

        visible.sort(key=lambda t: (t["done"], t["due"] or "9999-12-31"))

        for task in visible:
            checkbox = ft.Checkbox(
                value=task["done"],
                on_change=lambda e, t=task: toggle_task(e, t),
            )

            # A line through the text when the task is done.
            if task["done"]:
                line_style = ft.TextStyle(decoration=ft.TextDecoration.LINE_THROUGH)
                text_color = p["subtext"]
            else:
                line_style = None
                text_color = p["text"]

            task_text = ft.Text(task["text"], size=16, color=text_color, style=line_style)

            due_text, due_color = due_info(task)
            due_label = ft.Text(due_text, size=12, color=due_color)

            category_color = CATEGORIES[task["category"]]
            badge = ft.Container(
                content=ft.Text(task["category"], size=11, color="#FFFFFF",
                                weight=ft.FontWeight.BOLD),
                bgcolor=category_color,
                padding=ft.Padding(left=10, top=3, right=10, bottom=3),
                border_radius=10,
            )

            delete_button = ft.IconButton(
                icon=ft.Icons.DELETE_OUTLINE,
                icon_color=RED,
                tooltip="Delete task",
                on_click=lambda e, t=task: delete_task(t),
            )

            task_row = ft.Container(
                content=ft.Row(
                    controls=[
                        checkbox,
                        ft.Column([task_text, due_label], spacing=2, expand=True),
                        badge,
                        delete_button,
                    ],
                ),
                bgcolor=p["card"],
                padding=12,
                border_radius=12,
            )

            task_list.controls.append(task_row)

        update_summary()
        page.update()

    def apply_theme():
        p = colors()

        page.theme_mode = ft.ThemeMode.DARK if state["dark"] else ft.ThemeMode.LIGHT
        page.bgcolor = p["bg"]

        title_text.color = p["text"]
        subtitle_text.color = p["subtext"]
        task_count.color = p["subtext"]
        label_text.color = p["subtext"]
        add_label.color = p["subtext"]

        task_input.bgcolor = p["bg"]
        task_input.color = p["text"]

        content_card.bgcolor = p["card"]

        theme_button.icon = ft.Icons.LIGHT_MODE if state["dark"] else ft.Icons.DARK_MODE
        theme_button.icon_color = p["text"]

        update_date_button()
        render_filters()
        render_category_picker()
        render_tasks()

    def open_calendar(e):
        page.show_dialog(date_picker)  

    def date_chosen(e):
        picked = date_picker.value
        state["due"] = picked.strftime("%Y-%m-%d")  # save it as text, e.g. "2026-10-25"
        update_date_button()
        page.update()

    def clear_date(e):
        state["due"] = ""
        update_date_button()
        page.update()

    def add_task(e):
        text = task_input.value.strip()

        if not text:
            task_input.error = "Type a task first"
            page.update()
            return
        task_input.error = None

        tasks.append({
            "text": text,
            "done": False,
            "category": state["new_category"],
            "due": state["due"],
        })

        task_input.value = ""
        state["due"] = "" 
        update_date_button()
        render_tasks()

    def toggle_task(e, task):
        task["done"] = e.control.value
        render_tasks()

    def delete_task(task):
        tasks.remove(task)
        render_tasks()

    def set_filter(name):
        state["filter"] = name
        render_filters()
        render_tasks()

    def set_new_category(name):
        state["new_category"] = name
        render_category_picker()
        page.update()

    def toggle_theme(e):
        state["dark"] = not state["dark"]  # flip True <-> False
        apply_theme()

    task_input.on_submit = add_task  # pressing Enter adds the task
    date_button.on_click = open_calendar
    clear_date_button.on_click = clear_date
    date_picker.on_change = date_chosen
    theme_button.on_click = toggle_theme

    # ---------- LAYOUT ----------
    header = ft.Column(
        controls=[
            ft.Row(
                controls=[
                    ft.Column([title_text, subtitle_text], spacing=5),
                    theme_button,
                ],
                alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
            ),
            task_count,
            reminder_text,
        ],
        spacing=5,
    )

    add_row = ft.Row(
        controls=[
            task_input,
            date_button,
            clear_date_button,
            ft.Button(
                "Add",
                icon=ft.Icons.ADD,
                on_click=add_task,
                bgcolor="#4059AD",
                color="#FFFFFF",
            ),
        ],
    )

    content_card = ft.Container(
        content=ft.Column(
            controls=[
                label_text,
                add_row,
                ft.Row([add_label, category_row], spacing=10),
                ft.Divider(),
                filter_row,
                task_list,
            ],
            spacing=18,
        ),
        padding=22,
        border_radius=18,
    )

    page.add(
        ft.Column(
            controls=[header, content_card],
            spacing=25,
        )
    )

    apply_theme()  # paint everything for the first time


ft.run(main)