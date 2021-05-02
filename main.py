from flask import Flask, render_template, url_for, request, redirect
from werkzeug.utils import secure_filename
import cx_Oracle
import os

cx_Oracle.init_oracle_client(lib_dir="/Users/Alibek/Downloads/instantclient_19_8")
connection = cx_Oracle.connect('hr', 'oracle', 'localhost/orcl', encoding='UTF-8')

app = Flask(__name__)
app.config['UPLOAD_PATH'] = 'static/images'

@app.route("/", methods=['POST', 'GET'])
def index():
    cursor = connection.cursor()

    get_total_vac_people = cursor.callfunc('Func.get_total_vac_people', int, ['KAZ'])
    get_total_fully_vac_people = cursor.callfunc('Func.get_total_fully_vac_people', int, ['KAZ'])
    find_avg_daily_vacs = cursor.callfunc('Func.find_avg_daily_vacs', int, ['KAZ'])

    cursor.execute(f"select * from table(Func.vaccin)")
    vaccins = cursor.fetchall()



    if request.method == 'POST':
        cursor.execute(f"select * from table(Func.search_vacc(\'{request.form['search']}\'))")
        data_sets = cursor.fetchall()

        return render_template('index.html', data_sets=data_sets, get_total_vac_people=get_total_vac_people, get_total_fully_vac_people=get_total_fully_vac_people, find_avg_daily_vacs=find_avg_daily_vacs, vaccins=vaccins)
    else:
        cursor.execute("select * from table(test_package.test_plsql_table)")
        data_sets = cursor.fetchall()

        return render_template('index.html', data_sets=data_sets, get_total_vac_people=get_total_vac_people, get_total_fully_vac_people=get_total_fully_vac_people, find_avg_daily_vacs=find_avg_daily_vacs, vaccins=vaccins)


@app.route("/admin", methods=['GET', 'POST'])
def admin():
    cursor = connection.cursor()
    if request.method == 'POST':
        cursor.execute(f"select * from table(Func.search_vacc(\'{request.form['search']}\'))")
        data_sets = cursor.fetchall()

        return render_template('admin.html', data_sets=data_sets)
    else:
        cursor.execute("select * from table(test_package.test_plsql_table)")
        data_sets = cursor.fetchall()

        return render_template('admin.html', data_sets=data_sets)


@app.route("/countries")
def countries():
    cursor = connection.cursor()
    cursor.execute("select DISTINCT country from table(Pkg_Cur.Get_Raws2(CURSOR(SELECT * FROM VACS)))")
    countries = cursor.fetchall()

    return render_template('country.html', countries=countries)


@app.route("/insert", methods=['POST', 'GET'])
def insert():
    f = request.files['file']
    f.save(os.path.join(app.config['UPLOAD_PATH'], secure_filename(f.filename)))

    cursor = connection.cursor()
    cursor.execute(f"begin admin_pack.country_insert(:1, :2, TO_DATE(:3, 'dd.mm.yyyy'), :4, :5, :6, :7, :8, :9, :10, :11, :12, :13, :14, :15, :16, :17); end;", [
        str(request.form['country']),
        str(request.form['iso_code']),
        str(request.form['vaccination_date']),
        int(request.form['total_vaccinations']),
        int(request.form['people_vaccinated']),
        int(request.form['people_fully_vaccinated']),
        int(request.form['daily_vaccination_raw']),
        int(request.form['daily_vaccinations']),
        int(request.form['total_vaccination_per_hundred']),
        int(request.form['people_vaccination_per_hundred']),
        int(request.form['fully_vaccinated_per_hundred']),
        int(request.form['daily_vaccinations_per_million']),
        str(request.form['vaccines']),
        str(request.form['source_name']),
        str(request.form['source_website']),
        int(111),
        str(f.filename)
    ])
    print(request.form['vaccination_date'])
    connection.commit()


    return redirect('/admin')


@app.route("/update", defaults={'id': None}, methods=['GET', 'POST'])
@app.route("/update/<int:id>")
def update(id):
    if request.method == 'POST':
        f = request.files['file']
        f.save(os.path.join(app.config['UPLOAD_PATH'], secure_filename(f.filename)))

        cursor = connection.cursor()
        cursor.execute(f"begin admin_pack.country_update(:1, :2, TO_DATE(:3, 'dd.mm.yyyy'), :4, :5, :6, :7, :8, :9, :10, :11, :12, :13, :14, :15, :16, :17); end;", [
                str(request.form['country']),
                str(request.form['iso_code']),
                str(request.form['vaccination_date']),
                int(request.form['total_vaccinations']),
                int(request.form['people_vaccinated']),
                int(request.form['people_fully_vaccinated']),
                int(request.form['daily_vaccination_raw']),
                int(request.form['daily_vaccinations']),
                int(request.form['total_vaccination_per_hundred']),
                int(request.form['people_vaccination_per_hundred']),
                int(request.form['fully_vaccinated_per_hundred']),
                int(request.form['daily_vaccinations_per_million']),
                str(request.form['vaccines']),
                str(request.form['source_name']),
                str(request.form['source_website']),
                int(request.form['id']),
                str(f.filename)
            ])
        # connection.commit()

        return redirect('/admin')
    else:
        cursor = connection.cursor()
        cursor.execute('select * from vacs where country_id = :1', [id])
        vacs = cursor.fetchone()

        return render_template('update.html', vacs=vacs)


@app.route("/delete/<int:id>")
def delete(id):
    print(id)
    cursor = connection.cursor()
    cursor.execute("begin admin_pack.country_delete(:1); end;", [id])
    connection.commit()

    return redirect('/admin')


@app.route("/about")
def about():
    return render_template('about.html')


@app.route("/what")
def what():
    return render_template('what.html')


@app.route("/vac")
def vac():
    return render_template('vac.html')


if __name__ == "__main__":
    app.run(debug=True)