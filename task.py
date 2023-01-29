"""Template robot with Python."""
from RPA.Browser.Selenium import Selenium
from RPA.HTTP import HTTP
from RPA.PDF import PDF
from RPA.Archive import Archive
from RPA.Robocorp.Vault import Vault
import robot.libraries.Dialogs as Dialogs

import csv
import os

browser = Selenium()
vault = Vault()


def open_the_website():
    url = vault.get_secret('credentials')
    print(url['url_robot_website'])
    browser.open_available_browser(url['url_robot_website'])


def ask_for_the_csv_file_link():
    message = "Please provide the link to download the csv file"
    return Dialogs.get_value_from_user(message=message, default_value="https://...")


def close_popup_window():
    browser.click_button('css:.btn.btn-dark')


def download_the_csv_file(csv_link):
    http = HTTP()
    http.download(csv_link, overwrite=True)


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


def zip_orders_to_file():
    archive = Archive()
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
        open_the_website()
        close_popup_window()
        csv_file = ask_for_the_csv_file_link()
        # 'https://robotsparebinindustries.com/orders.csv'
        download_the_csv_file(csv_file)
        fill_and_submit_the_form_using_the_data_from_the_csv_file()
        zip_orders_to_file()
        Dialogs.MessageDialog(
            "Robot generated the whole tasks succesfully").show()

    finally:
        browser.close_all_browsers()

    print("Done.")


if __name__ == "__main__":
    main()
