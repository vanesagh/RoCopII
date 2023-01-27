"""Template robot with Python."""
from RPA.Browser.Selenium import Selenium
from RPA.HTTP import HTTP
from RPA.PDF import PDF
from RPA.Archive import Archive
from RPA.Dialogs import Dialogs

import csv
import os

browser = Selenium()
dialogs = Dialogs()


def open_the_website(url):
    browser.open_available_browser(url)


def ask_for_the_csv_file_link():
    dialogs.add_heading("Some text")
    dialogs.add_text("Empty space")
    # dialogs.add_text_input(
    #    name="csv_file", label="csv_file", placeholder="insert url", rows=5)
    # result = dialogs.run_dialog()
    dialogs.run_dialog()
   # print(result.csv_file)


def close_popup_window():
    browser.click_button('css:.btn.btn-dark')


def download_the_csv_file():
    http = HTTP()
    http.download(
        'https://robotsparebinindustries.com/orders.csv', overwrite=True)


def fill_the_form(body, head, legs, address):
    browser.select_from_list_by_value("id:head", head)
    browser.click_element("id:id-body-" + body)
    id_number = browser.get_element_attribute(
        "//input[@placeholder='Enter the part number for the legs']", "id")
    browser.input_text("id:" + id_number, legs)
    browser.input_text("id:address", address)


def capture_screenshot_of_preview_and_order(order_number):
    browser.capture_element_screenshot("css:div#robot-preview-image",
                                       filename=f"{os.getcwd()}/output/robot_img_{order_number}.png")

    receipt_html = browser.get_element_attribute("id:receipt", "outerHTML")
    pdf = PDF()
    pdf.html_to_pdf(receipt_html, f"./output/receipt_{order_number}.pdf")
    pdf.add_files_to_pdf(files=[f"./output/receipt_{order_number}.pdf",
                                f"./output/robot_img_{order_number}.png:align=center"],
                         target_document=f"./output/orders/order_number_{order_number}.pdf")


def zip_orders_to_file(order_file):
    archive = Archive()
    print(order_file)
    archive.archive_folder_with_zip("./output/orders", "./output/orders.zip")


def fill_and_submit_the_form_for_one_order(body, head, legs, address, order_number):
    if browser.is_element_visible('css:.btn.btn-dark'):
        print("close pop-up")
        close_popup_window()
    fill_the_form(body, head, legs, address)
    browser.click_button("id:preview")
    browser.click_button("id:order")

    while browser.is_element_visible("css:.alert.alert-danger"):
        browser.double_click_element("id:order")
        print("alert something went wrong with the web page")
        if browser.is_element_visible('css:.btn.btn-dark'):
            print("close pop-up and alert")
            close_popup_window()
            fill_the_form(body, head, legs, address)
            browser.click_button("id:preview")
            browser.click_button("id:order")

    if browser.is_element_visible('id:order-another'):
        capture_screenshot_of_preview_and_order(order_number)
    browser.click_button_when_visible("id:order-another")


def fill_and_submit_the_form_using_the_data_from_the_csv_file():
    with open("orders.csv") as csv_file:
        csv_reader = csv.DictReader(csv_file)
        for row in csv_reader:
            fill_and_submit_the_form_for_one_order(row['Body'], row['Head'], row['Legs'], row['Address'],
                                                   row['Order number'])


def main():
    try:
        open_the_website("https://robotsparebinindustries.com/#/robot-order")
        close_popup_window()
        ask_for_the_csv_file_link()
        download_the_csv_file()
        fill_and_submit_the_form_using_the_data_from_the_csv_file()
        zip_orders_to_file("./output/orders/order_number_1.pdf")

    finally:
        browser.close_all_browsers()

    print("Done.")


if __name__ == "__main__":
    main()