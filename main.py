
import flet as ft

#Part 1

def main(page: ft.Page):
    first_name = ft.TextField(label="Enter first name")
    last_name = ft.TextField(label="Enter last name")

    result = ft.Text()

    def show_input(e):
        result.value = "Hello, " + first_name.value + " " + last_name.value
        page.update()

    page.add(
        first_name,
        last_name,
        ft.Button("Submit", on_click=show_input),
        result
    )



#------------------------------------------ Part 2 in Main.py ------------------------------------------

# import random

# def main(page: ft.Page):
#     def change_color(e):
#         colors = ["red", "blue", "green", "yellow", "purple", "pink", "orange"]
#         page.bgcolor = random.choice(colors)
#         page.update()

#     page.add(
#         ft.Text("Random Background Color", size=25),
#         ft.Button("Change Color", on_click=change_color)
#     )



# def main(page: ft.Page):
#     page.title = "Nada"
#     page.bgcolor = "green"

#     page.add(
#         ft.Text("First app",color="red", size=30, weight=ft.FontWeight.BOLD)
#     )



ft.run(main)
