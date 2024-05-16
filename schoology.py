import requests
import re
from bs4 import BeautifulSoup

class Schoology:
    def __init__(self, api_key):
        self.api_key = api_key
        self.session = requests.Session()
        self.headers = {
            "Cookie": self.api_key
        }

    def get_courses(self):
        url = "https://cole.cherrycreekschools.org/courses"
        response = self.session.get(url, headers=self.headers)
        soup = BeautifulSoup(response.text, "html.parser")
        courses = [(course.find("a")["href"].split("/")[-1], course.find("span", class_="course-title").text)
                   for course in soup.find_all("li", class_="course-item list-item")]
        return courses

    def get_member_info(self, member_id):
        url = f"https://cole.cherrycreekschools.org/user/{member_id}/info"
        response = self.session.get(url, headers=self.headers)
        soup = BeautifulSoup(response.text, "html.parser")
        name = soup.find("h2", class_="page-title").text.strip()
        email = None
        phone = None
        """tbl = soup.find("table", class_="info-tab")
        trs = tbl.find("tbody").find_all("tr")
        for tr in trs:
            if "Email" in tr.text:
                email = tr.find("td").text
            if "Phone" in tr.text:
                phone = tr.find("td").text
        if phone is not None:
            phone = re.sub(r"\D", "", phone)
            if phone.startswith("1 "):
                phone = phone[1:]
            phone = f"({phone[:3]})-{phone[3:6]}-{phone[6:]}"
        """
        return {"name": name, "email": email, "phone": phone}

    def get_members(self, course_id):
        url = f"https://cole.cherrycreekschools.org/enrollments/edit/members/course/{course_id}/ajax?ss=&p=1"
        response = self.session.get(url, headers=self.headers)
        soup = BeautifulSoup(response.text, "html.parser")
        count = soup.find("div", class_="enrollment-view-nav").find('div', class_='count')
        pages = int(count.find('span', class_='total').text) // int(count.find('span', class_='end-count').text)
        members = []
        for page in range(1, pages + 1):
            url = f"https://cole.cherrycreekschools.org/enrollments/edit/members/course/{course_id}/ajax?ss=&p={page}"
            response = self.session.get(url, headers=self.headers)
            soup = BeautifulSoup(response.text, "html.parser")
            for member in soup.find_all('td', class_="user-name"):
                member_id = member.find("a")["href"].split("/")[-1]
                members.append(member_id)
        return members
