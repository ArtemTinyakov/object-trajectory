import flet as ft
import numpy as np


stop = False


def is_number(page, flet_container, coef=1.):
    try:
        res = float(flet_container.value)*coef
        return res
    except ValueError:
        flet_container.error_text = "некорректный ввод"
        page.update()
        return None


def calculate_and_draw_trajectory(page, points, injector_points, chart, mass, velocity, conveyor_height, injector_x, injector_y, angle, injector_pulse, injector_diameter, object_length):
    global stop
    chart.max_x = 4
    chart.max_y = 3
    injector_work_time = 0
    mass_ = is_number(page, mass)
    velocity_ = is_number(page, velocity)
    conveyor_height_ = is_number(page, conveyor_height)
    injector_x_ = is_number(page, injector_x)
    injector_y_ = is_number(page, injector_y)
    angle_ = is_number(page, angle, np.pi/180)
    injector_pulse_ = is_number(page, injector_pulse)
    injector_diameter_ = is_number(page, injector_diameter, 0.001)
    object_length_ = is_number(page, object_length, 0.001)

    if not mass_ or not velocity_ or not conveyor_height_ or not injector_x_ or not injector_y_ or not angle_ or not injector_pulse_ or not injector_diameter_ or not object_length_:
        return

    if angle_ < 0 or angle_ > 90:
        angle.error_text = "угол должен быть от 0 до 90"
        page.update()
        return

    g = 9.81
    x, y = 0, conveyor_height_
    ux, uy = velocity_, 0
    dt = 1e-3
    t = 0

    x_h = injector_x_ - object_length_ / 2 * np.cos(np.pi / 2 - angle_)
    y_h = injector_y_ + object_length_ / 2 * np.sin(np.pi / 2 - angle_)
    x_l = injector_x_ + object_length_ / 2 * np.cos(np.pi / 2 - angle_)
    y_l = injector_y_ - object_length_ / 2 * np.sin(np.pi / 2 - angle_)

    injector_points.data_points.append(ft.LineChartDataPoint(x_h, y_h))
    injector_points.data_points.append(ft.LineChartDataPoint(x_l, y_l))
    injector_points.data_points.append(ft.LineChartDataPoint(x_l + 10*injector_diameter_*np.cos(angle_), y_l + 10*injector_diameter_*np.sin(angle_)))
    injector_points.data_points.append(ft.LineChartDataPoint(x_h + 10*injector_diameter_*np.cos(angle_), y_h + 10*injector_diameter_*np.sin(angle_)))
    injector_points.data_points.append(ft.LineChartDataPoint(x_h, y_h))
    page.update()

    while y > 0 and x < 10:
        if stop:
            stop = False
            return injector_work_time
        if y > chart.max_y:
            chart.max_y += 2
        if x > chart.max_x:
            chart.max_x += 2
        t += dt
        uy += dt*g
        if ((x - injector_x_) ** 2 + (y - injector_y_) ** 2) ** 0.5 < 10 * injector_diameter_:
            if 1 / np.tan(np.pi / 2 - angle_) * (x - x_h) + y_h > y > 1 / np.tan(np.pi / 2 - angle_) * (x - x_l) + y_l:
                injector_work_time += dt
                ux += dt * injector_pulse_ * np.cos(angle_) / mass_
                uy -= dt * injector_pulse_ * np.sin(angle_) / mass_

        x += dt * ux
        y -= uy * dt + g * dt ** 2 / 2
        points.data_points.append(ft.LineChartDataPoint(x, y))
        page.update()
    return injector_work_time


def main(page: ft.Page):
    def btn_click(e):
        if mass.value and velocity.value and conveyor_height.value and injector_x.value and injector_y.value and angle.value and injector_pulse.value and injector_diameter.value and object_length.value:
            error_message.value = ""
            exposure_time.value = ""
            points.data_points.clear()
            injector_points.data_points.clear()
            page.update()
            injector_work_time = calculate_and_draw_trajectory(page, points, injector_points, chart, mass, velocity, conveyor_height, injector_x, injector_y, angle, injector_pulse, injector_diameter, object_length)
            exposure_time.value = f"форсунка воздействовала на объект {int(injector_work_time*1000)} мс"
            page.update()
        else:
            error_message.value = "вы заполнили не все поля"
            page.update()

    def stop_btn_click(e):
        global stop
        stop = True

    def clear_btn_click(e):
        points.data_points.clear()
        injector_points.data_points.clear()
        exposure_time.value = ""
        error_message.value = ""
        page.update()

    mass = ft.TextField(label="масса объекта, кг", autofocus=True, hint_text="0.1", color="orange")
    velocity = ft.TextField(label="скорость ленты, м/сек", autofocus=True, hint_text="0.4", color="orange")
    conveyor_height = ft.TextField(label="высота ленты, м", autofocus=True, hint_text="1", color="orange")
    injector_x = ft.TextField(label="x форсунки, м", autofocus=True, hint_text="0.1", color="orange")
    injector_y = ft.TextField(label="y форсунки, м", autofocus=True, hint_text="0.6", color="orange")
    angle = ft.TextField(label="угол наклона форсунки, градусы", autofocus=True, hint_text="60", color="orange")
    injector_pulse = ft.TextField(label="импульс форсунки, кг*м/с", autofocus=True, hint_text="13", color="orange")
    injector_diameter = ft.TextField(label="диаметр выходного сечения, мм", autofocus=True, hint_text="10", color="orange")
    object_length = ft.TextField(label="длина участка обдувания, мм", autofocus=True, hint_text="30", color="orange")
    button = ft.ElevatedButton(text="построить график", on_click=btn_click, color="orange")
    button_stop = ft.ElevatedButton(text="остановить", on_click=stop_btn_click, color="orange")
    button_clear = ft.ElevatedButton(text="очистить", on_click=clear_btn_click, color="orange")
    exposure_time = ft.Text(color="orange")
    error_message = ft.Text(color="red")

    settings = ft.Column(controls=[mass, velocity, conveyor_height, injector_x, injector_y, angle, injector_pulse, injector_diameter, object_length, button, ft.Row([button_stop, button_clear]), exposure_time, error_message], expand=False, horizontal_alignment=ft.CrossAxisAlignment.CENTER, wrap=True)

    points = ft.LineChartData(stroke_width=3, color=ft.colors.PINK, curved=True, stroke_cap_round=True,)

    injector_points = ft.LineChartData(stroke_width=3, color=ft.colors.BLUE)

    x_labels = [ft.ChartAxisLabel(value=i/10,
                                  label=ft.Container(
                                      ft.Text(value=f"{i/10}m",
                                              weight=ft.FontWeight.BOLD,
                                              color="orange",
                                              size=10, ),
                                      margin=ft.margin.only(top=15), ),
                                  ) for i in range(101)]

    y_labels = [ft.ChartAxisLabel(value=i/10,
                                  label=ft.Container(
                                      ft.Text(value=f"{i/10}m",
                                              weight=ft.FontWeight.BOLD,
                                              color="orange",
                                              size=10, ),
                                      margin=ft.margin.only(right=15), ),
                                  ) for i in range(101)]

    chart = ft.LineChart(
        left_axis=ft.ChartAxis(
            labels=y_labels,
            labels_size=40,
        ),
        bottom_axis=ft.ChartAxis(
            labels=x_labels,
            labels_size=40,
        ),
        data_series=[injector_points, points],
        horizontal_grid_lines=ft.ChartGridLines(
            interval=0.1, color=ft.colors.with_opacity(0.2, ft.colors.ON_SURFACE), width=1,
        ),
        vertical_grid_lines=ft.ChartGridLines(
            interval=0.1, color=ft.colors.with_opacity(0.2, ft.colors.ON_SURFACE), width=1,
        ),
        tooltip_bgcolor=ft.colors.with_opacity(0.9, ft.colors.BLUE_GREY),
        min_y=0,
        max_y=3,
        min_x=0,
        max_x=4,
        expand=True,
    )

    page.title = "расчёт траектории объекта"
    page.add(ft.Row([settings, chart], vertical_alignment=ft.CrossAxisAlignment.CENTER, expand=True, alignment=ft.MainAxisAlignment.CENTER))


ft.app(main)#, view=ft.AppView.WEB_BROWSER)
