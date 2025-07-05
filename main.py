from fastapi import FastAPI, Request, Form
from fastapi.templating import Jinja2Templates
from faker import Faker
import random
import uvicorn
import datetime

app = FastAPI()
templates = Jinja2Templates(directory="templates")


def generate_random_user(
        locale: str = "en_US",
        gender: str = "any",
        include_education: bool = False,
        include_avatar: bool = False,
        include_medical: bool = False,
        include_financial: bool = False,
        include_interests: bool = False
):
    faker = Faker(locale)

    # Определение пола
    if gender == "any":
        gender = random.choice(["male", "female"])

    # Генерация имени
    if gender == "male":
        first_name = faker.first_name_male()
        last_name = faker.last_name_male()
    else:
        first_name = faker.first_name_female()
        last_name = faker.last_name_female()

    full_name = f"{first_name} {last_name}"
    initials = f"{first_name[0]}{last_name[0]}"

    # Генерация основных данных
    fake_date_of_b = faker.date_of_birth(minimum_age=18, maximum_age=90)
    user = {
        "name": full_name,
        "initials": initials,
        "first_name": first_name,
        "last_name": last_name,
        "gender": "Мужской" if gender == "male" else "Женский",
        "birthdate": fake_date_of_b.strftime("%d.%m.%Y"),
        "age": datetime.datetime.now().year - fake_date_of_b.year,
        "email": faker.email(),
        "phone": faker.phone_number(),
        "job": faker.job(),
        "company": faker.company(),
        "username": faker.user_name(),
        "password": faker.password(length=12),
        "website": faker.url(),
    }

    # Форматированный адрес
    address_data = {
        "street": faker.street_address(),
        "city": faker.city(),
        "zipcode": faker.postcode(),
        "country": faker.country(),
        "coordinates": (faker.latitude(), faker.longitude())
    }
    user[
        "address"] = f"{address_data['street']}, {address_data['city']}, {address_data['zipcode']}, {address_data['country']}"
    user["address_data"] = address_data

    # Аватар
    if include_avatar:
        user["avatar"] = f"https://i.pravatar.cc/300?u={faker.uuid4()}"

    # Документы
    user["id_number"] = faker.ssn()

    # Социальные сети
    user["social"] = {
        "facebook": f"facebook.com/{faker.user_name()}",
        "twitter": f"twitter.com/{faker.user_name()}",
        "instagram": f"instagram.com/{faker.user_name()}",
        "linkedin": f"linkedin.com/in/{faker.user_name()}"
    }

    # Образование
    if include_education:
        user["education"] = {
            "major": faker.job(),
            "year": random.randint(1990, datetime.datetime.now().year)
        }
    else:
        user["education"] ={
            "major":"",
            "year":"No education"
        }


    # Медицинские данные
    if include_medical:
        user["medical"] = {
            "allergies": [faker.word() for _ in range(random.randint(1, 3))],
            "height": f"{random.randint(150, 200)} см",
            "weight": f"{random.randint(50, 120)} кг"
        }

    # Финансовые данные
    if include_financial:
        user["financial"] = {
            "bank": faker.iban(),
            "credit_card": faker.credit_card_full(),
            "currency": faker.currency_code(),
            "salary": f"{random.randint(20000, 200000)} {faker.currency_code()}/год"
        }

    # Интересы
    if include_interests:
        user["interests"] = [faker.word() for _ in range(random.randint(3, 8))]

    # Семейное положение
    user["family"] = {
        "status": random.choice(["Холост", "Женат", "Разведен", "Вдовец"]),
        "children": random.randint(0, 3)
    }

    # История работы
    user["employment_history"] = [
        {
            "company": faker.company(),
            "position": faker.job(),
            "duration": f"{random.randint(1, 8)} лет",
            "period": f"{random.randint(1990, 2020)}-{random.randint(1995, 2023)}"
        } for _ in range(random.randint(1, 3))
    ]

    return user


@app.get("/")
async def user_generator_form(request: Request):
    return templates.TemplateResponse("generator.html", {"request": request})


@app.post("/generate")
async def generate_users(
        request: Request,
        count: int = Form(5, ge=1, le=100),
        gender: str = Form("any"),
        locale: str = Form("en_US"),
        include_education: bool = Form(False),
        include_avatar: bool = Form(False),
        include_medical: bool = Form(False),
        include_financial: bool = Form(False),
        include_interests: bool = Form(False)
):
    users = []
    for _ in range(count):
        user = generate_random_user(
            locale=locale,
            gender=gender,
            include_education=include_education,
            include_avatar=include_avatar,
            include_medical=include_medical,
            include_financial=include_financial,
            include_interests=include_interests
        )
        users.append(user)


    locale_names = {
        "en_US": "Английский (США)",
        "ru_RU": "Русский",
        "de_DE": "Немецкий",
        "fr_FR": "Французский",
        "ja_JP": "Японский",
        "es_ES": "Испанский"
    }

    gender_names = {
        "any": "Любой",
        "male": "Мужской",
        "female": "Женский"
    }

    return templates.TemplateResponse("results.html", {
        "request": request,
        "users": users,
        "count": count,
        "locale_name": locale_names.get(locale, locale),
        "gender_name": gender_names.get(gender, gender),
        "timestamp": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    })

if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="127.0.0.1",
        port=8000,
    )

