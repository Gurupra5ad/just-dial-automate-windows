import csv
import requests
import tkinter as tk
from bs4 import BeautifulSoup


def innerHTML(element):
    return element.decode_contents(formatter="html")

def get_name(body):
	return body.find('span', {'class':'jcn'}).a.string

def which_digit(html):
    mappingDict={'icon-ji':9,
                'icon-lk':8,
                'icon-nm':7,
                'icon-po':6,
                'icon-rq':5,
                'icon-ts':4,
                'icon-vu':3,
                'icon-wx':2,
                'icon-yz':1,
                'icon-acb':0,
                }
    return mappingDict.get(html,'')

def get_phone_number(body):
    i=0
    phoneNo = "No Number!"
    try:
            
        for item in body.find('p',{'class':'contact-info'}):
            i+=1
            if(i==2):
                phoneNo=''
                try:
                    for element in item.find_all(class_=True):
                        classes = []
                        classes.extend(element["class"])
                        phoneNo+=str((which_digit(classes[1])))
                except:
                    pass
    except:
        pass
    body = body['data-href']
    soup = BeautifulSoup(body, 'html.parser')
    for a in soup.find_all('a', {"id":"whatsapptriggeer"} ):
        # print (a)
        phoneNo = str(a['href'][-10:])


    return phoneNo

def get_tags(body):
	return body.find('span', {'class':'margin0'}).text.strip()

def get_address(body):
	return body.find('span', {'class':'mrehover'}).text.strip()


def get_location(body):
	text = body.find('a', {'class':'rsmap'})
	if text == None:
		return
	text_list = text['onclick'].split(",")
	
	latitutde = text_list[3].strip().replace("'", "")
	longitude = text_list[4].strip().replace("'", "")
	
	return latitutde + ", " + longitude


def scrape(entry):
    
    page_number = 1
    service_count = 1

    fields = ['Name', 'Phone', 'Address', 'Location']


    out_file = open('data.csv','w')
    csvwriter = csv.DictWriter(out_file, delimiter=',', fieldnames=fields)

    # Write fields first
    csvwriter.writerow(dict((fn,fn) for fn in fields))

    while True:

        # Check if reached end of result
        if page_number > 10:
            break
        session = requests.Session()
        session.headers.update({"User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/78.0.3904.108 Safari/537.36"})
        url=entry+"-%s" % (page_number)


        r = session.get(url); 

        soup = BeautifulSoup(r.content, "lxml")
        services = soup.find_all('li', {'class': 'cntanr'})


        # Iterate through the 10 results in the page
        for service_html in services:

            # Parse HTML to fetch data
            dict_service = {}
            name = get_name(service_html)
            phone = get_phone_number(service_html)
            address = get_address(service_html)
            location = get_location(service_html)
            if name != None:
                dict_service['Name'] = name
            if phone != None:
                print('getting phone number')
                dict_service['Phone'] = phone
            if address != None:
                dict_service['Address'] = address
            if location != None:
                dict_service['Location'] = location

            # Write row to CSV
            csvwriter.writerow(dict_service)


            data = {}

            print("#" + str(service_count) + " " , dict_service)
            service_count += 1

        page_number += 1

    out_file.close()
    label['text'] = "Execution Done"


HEIGHT = 700
WIDTH = 800

root = tk.Tk()

root.title("Just-Dial Scraper")

canvas = tk.Canvas(root, height=HEIGHT, width=WIDTH, bg="#a58faa")
canvas.pack()

frame = tk.Frame(root, bg="#ededd0",bd=5)
frame.place(relx=0.5, rely=0.25, relwidth=0.75, relheight=0.1, anchor="n")

entry = tk.Entry(frame, font=("Times", 15))
entry.place(relwidth=0.65, relheight=1)

button = tk.Button(frame, font=("Times", 15), text="Submit", bg="#a58faa", command= lambda: scrape(entry.get()))
button.place(relx=0.7, relheight=1, relwidth=0.3)

lower_frame = tk.Frame(root, bg="#ededd0",bd=10)
lower_frame.place(relx=0.5, rely=0.40, relwidth=0.75, relheight=0.5,anchor="n")

label = tk.Label(lower_frame, font=("Times", 30))
label.place(relwidth=1, relheigh=1)
root.mainloop()
