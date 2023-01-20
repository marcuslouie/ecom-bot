import json
from random import choice
import string


class Invmanager:
    def __init__(self):
        self.self = None

    def create_product(self, name, product, stock, price, MSRP, link, photo):
        product = str(product).title()
        inventory = Invmanager().stock_data()
        if product in inventory:
            print('item is already in inventory!')
            return False
        else:
            inventory[product] = {}
            inventory[product]['name'] = name
            inventory[product]['stock'] = stock
            inventory[product]['price'] = price
            inventory[product]['MSRP'] = MSRP
            inventory[product]['link'] = link
            inventory[product]['photo'] = photo

        with open('inventory.json', 'w') as f:
            json.dump(inventory, f)
            return True

    def stock_data(self):
        with open('inventory.json', 'r') as f:
            inventory = json.load(f)

        return inventory

    def edit_product(self, product, data, value):
        inventory = Invmanager().stock_data()
        if product in inventory:
            if data in inventory[product]:
                inventory[product][data] = value

                with open('inventory.json', 'w') as f:
                    json.dump(inventory, f)
            else:
                "Attribute doesn't exist"
        else:
            "Product doesn't exist"

    def edit2(self, name, product, stock, price, MSRP, link, photo):
        product = str(product).title()
        inventory = Invmanager().stock_data()
        if product in inventory:
            if name is not None:
                inventory[product]['name'] = stock
            if stock is not None:
                inventory[product]['stock'] = stock
            if price is not None:
                inventory[product]['price'] = price
            if MSRP is not None:
                inventory[product]['MSRP'] = MSRP
            if link is not None:
                inventory[product]['link'] = link
            if photo is not None:
                inventory[product]['photo'] = photo
            with open('inventory.json', 'w') as f:
                json.dump(inventory, f)
                return True
        else:
            print("item doesn't exist")
            return False

    def delete_product(self, product):
        inventory = Invmanager().stock_data()
        if product in inventory:
            del inventory[product]

            with open('inventory.json', 'w') as f:
                json.dump(inventory, f)
        else:
            print("Product doesn't exist")

    def order_data(self):
        with open('orders.json', 'r') as f:
            orders = json.load(f)

        return orders

    def create_order(self, product, quantity, orderer):
        orders = Invmanager().order_data()
        order_number = Invmanager().generate_code()
        if order_number not in orders:
            orders[order_number] = {}
            orders[order_number]['product'] = product
            orders[order_number]['quantity'] = quantity
            orders[order_number]['status'] = 'Pending'
            orders[order_number]['tracking_no'] = 'Currently no tracking number'
            orders[order_number]['orderer'] = orderer
            with open('orders.json', 'w') as f:
                json.dump(orders, f)
        return order_number

    def edit_order(self, order_number, data, value):
        orders = Invmanager().order_data()
        if order_number in orders:
            if data in orders[order_number]:
                orders[order_number][data] = value

                with open('orders.json', 'w') as f:
                    json.dump(orders, f)
            else:
                print('order2 fail')
        else:
            print('order1 fail')

    def generate_code(self, length=8, chars=string.ascii_lowercase+string.digits):
        return ''.join([choice(chars) for i in range(length)])

    def view_order(self, order_number):
        orders = Invmanager().order_data()
        return orders[order_number]
