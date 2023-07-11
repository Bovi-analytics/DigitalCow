import datetime

from cow_builder import digital_cow, digital_herd

if __name__ == '__main__':
    herd_id = 1329
    # url = f"https://animals.mmmooogle.com/api/v1/herds/" \
    #       f"{herd_id}/active-animals/"
    # user = input("username: ")
    # password = input("password: ")
    # req_token_url = ""
    # oauth = OAuth1Session(user, client_secret=password)
    # fetch_response = oauth.fetch_request_token(url)
    # owner_key, owner_secret = fetch_response.get(['oauth_token', 'oauth_secret'])
    # owner_key = fetch_response.get('oauth_token')
    # owner_secret = fetch_response.get('oauth_secret')
    # auth = OAuth1(user, password)

    # url_ = f"https://animals.mmmooogle.com/api/v1/animals/" \
    #        f"{cow['AnimalId']}/pregnancydiagnoses"
    # last_pregnancy = requests.get(url_).json()[-1]["StartDate"]
    #
    # request = requests.get(url=url, auth=auth)
    # data = request.json()
    # print(data)
    data = [
        # insert data
    ]
    print(f"number of cows on farm: {len(data)}")
    herd = digital_herd.DigitalHerd()
    dim = None
    ln = None
    for cow in data:
        try:
            dim = (datetime.datetime.today() - datetime.datetime.strptime(
                cow["LastCalvingDate"], '%Y-%m-%dT%H:%M:%S')).days
        except KeyError as error:
            if error.args[0] == "LastCalvingDate":
                dim = (datetime.datetime.today() - datetime.datetime.strptime(
                    cow["BirthDate"], '%Y-%m-%dT%H:%M:%S')).days
        age = (datetime.datetime.today() - datetime.datetime.strptime(
            cow["BirthDate"], '%Y-%m-%dT%H:%M:%S')).days
        try:
            ln = cow["Parity"]
        except KeyError as error:
            if error.args[0] == "Parity":
                ln = 0
        match cow["CurrentStatus"]:
            # 0: None
            # 1: Open
            # 3: Served
            # 4: Not Pregnant
            # 5: Pregnant
            # 6: Barren
            # 7: Aborted
            # 8: Dry
            # 9: Sold
            # 10: Dead
            case 0 | 1 | 3 | 4:
                state = 'Open'
                dp = 0
            case 5:
                state = 'Pregnant'
                dp = (datetime.datetime.today() - datetime.datetime.strptime(
                    cow["StatusDate"], '%Y-%m-%dT%H:%M:%S')).days
            case 8:
                state = 'Pregnant'
                dp = (datetime.datetime.today() - datetime.datetime.strptime(
                    cow["StatusDate"], '%Y-%m-%dT%H:%M:%S')).days
                dp += 220
            case 6:
                state = 'DoNotBreed'
                dp = 0
            case 7:
                vwp = herd.get_voluntary_waiting_period(ln)
                insemination_window = herd.get_insemination_window(ln)
                if dim < vwp + insemination_window:
                    state = 'Open'
                else:
                    state = 'DoNotBreed'
                dp = 0
            case 9 | 10:
                state = 'Exit'
                dp = 0
            case _:
                state = None
                dp = 0

        new_cow = digital_cow.DigitalCow(dim, ln, dp, 160, 140, 3.4, age, herd, state)

    for cow in herd.herd:
        print(str(cow))
    print("success")
