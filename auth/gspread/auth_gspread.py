import gspread

def authenticate_gspread(worksheet_name):
    gc = gspread.oauth(
        credentials_filename='./auth/gspread/credentials.json',
        authorized_user_filename='./auth/gspread/authorized_user.json'
    )
    sh = gc.open("Trading Log")

    return sh.worksheet(worksheet_name)
