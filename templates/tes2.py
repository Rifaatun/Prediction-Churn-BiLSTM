from flask import Flask, render_template, request, redirect, url_for, session, flash
import pandas as pd
from flask_mysqldb import MySQL
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from flask_bcrypt import Bcrypt

app = Flask(__name__)
app.secret_key= 'your-secret-key'

# Initialize Bcrypt
bcrypt = Bcrypt(app)

#Meghubungkan Mysql
app.config['MYSQL_HOST'] ='localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = ''
app.config['MYSQL_DB'] = 'klasifikasi'

mysql = MySQL(app)

mappingPekerjaanAyah = {
    'TIDAK BEKERJA': 0,
    'Petani': 1,
    'Nelayan': 2,
    'PNS': 3,
    'Wirausaha': 4,
    'Peg. Swasta': 5,
    'TNI / POLRI': 6,
    'Lainnya': 7
}

mappingPenghasilanAyah = {
    'Tidak Berpenghasilan': 0,
    '< Rp. 250.000': 1,
    'Rp. 250.001 - Rp. 500.000': 2,
    'Rp. 500.001 - Rp. 750.000': 3,
    'Rp. 750.001 - Rp. 1.000.000': 4,
    'Rp. 1.000.001 - Rp. 1.250.000': 5,
    'Rp. 1.250.001 - Rp. 1.500.000': 6,
    'Rp. 1.500.001 - Rp. 1.750.000': 7,
    'Rp. 1.750.001 - Rp. 2.000.000': 8,
    'Rp. 2.000.001 - Rp. 2.250.000': 9,
    'Rp. 2.250.001 - Rp. 2.500.000': 10,
    'Rp. 2.500.001 - Rp. 2.750.000': 11,
    'Rp. 2.750.001 - Rp. 3.000.000': 12,
    'Rp. 3.000.001 - Rp. 3.250.000': 13,
    'Rp. 3.250.001 - Rp. 3.500.000': 14,
    'Rp. 3.500.001 - Rp. 3.750.000': 15,
    'Rp. 3.750.001 - Rp. 4.000.000': 16,
    'Rp. 4.000.001 - Rp. 4.250.000': 17,
    'Rp. 4.250.001 - Rp. 4.500.000': 18,
    'Rp. 4.500.001 - Rp. 4.750.000': 19,
    'Rp. 4.750.001 - Rp. 5.000.000': 20,
    'Rp. 5.000.001 - Rp. 5.250.000': 21,
    'Rp. 5.250.001 - Rp. 5.500.000': 22,
    'Rp. 5.500.001 - Rp. 5.750.000': 23
}

mappingStatusAyah = {
    'Wafat': 0,
    'Hidup': 1,
    'Bercerai': 2
}

mappingPekerjaanIbu = {
    'TIDAK BEKERJA': 0,
    'Petani': 1,
    'Wirausaha': 2,
    'Peg. Swasta': 3,
    'PNS': 4,
    'Lainnya': 5,
}

mappingPenghasilanIbu = {
    'Tidak Berpenghasilan' : 0,
    '< Rp. 250.000': 1,
    'Rp. 250.001 - Rp. 500.000': 2,
    'Rp. 500.001 - Rp. 750.000': 3,
    'Rp. 750.001 - Rp. 1.000.000': 4,
    'Rp. 1.000.001 - Rp. 1.250.000': 5,
    'Rp. 1.250.001 - Rp. 1.500.000': 6,
    'Rp. 1.500.001 - Rp. 1.750.000': 7,
    'Rp. 1.750.001 - Rp. 2.000.000': 8,
    'Rp. 2.000.001 - Rp. 2.250.000': 9,
    'Rp. 2.250.001 - Rp. 2.500.000': 10,
    'Rp. 2.500.001 - Rp. 2.750.000': 11,
    'Rp. 2.750.001 - Rp. 3.000.000': 12,
    'Rp. 3.000.001 - Rp. 3.250.000': 13,
    'Rp. 3.250.001 - Rp. 3.500.000': 14,
    'Rp. 3.500.001 - Rp. 3.750.000': 15,
    'Rp. 3.750.001 - Rp. 4.000.000': 16,
    'Rp. 4.000.001 - Rp. 4.250.000': 17,
    'Rp. 4.250.001 - Rp. 4.500.000': 18,
    'Rp. 4.500.001 - Rp. 4.750.000': 19,
    'Rp. 4.750.001 - Rp. 5.000.000': 20,
    'Rp. 5.000.001 - Rp. 5.250.000': 21,
    'Rp. 5.250.001 - Rp. 5.500.000': 22
}

mappingStatusIbu = {
    'Hidup': 1,
    'Wafat': 0,
}

mappingKepemilikanRumah = {
    'Tidak Memiliki': 0,
    'Menumpang Tanpa Ijin': 1,
    'Menumpang': 2,
    'Sewa Bulanan': 3,
    'Sewa Tahunan': 4,
    'Sendiri': 5
}

mappingSumberAir = {
    'Sumur': 0,
    'Sungai/Mata Air': 1,
    'PDAM': 2,
    'Kemasan': 3
}

mappingBiayaListrikBulanan = {
    50000: 0,
    100000: 1,
    150000: 2,
    200000: 3,
    250000: 4,
    300000: 5
}

mappingKondisiRumah = {
    'Buruk': 0,
    'Sedang': 1,
    'Baik': 2
}

def extract_number(string):
    try:
        return int(string.split()[0])
    except (ValueError, AttributeError):
        return 0

def convertPekerjaanAyah(pa):
    role = {
        0: "TIDAK BEKERJA",
        1: "Petani",
        2: "Nelayan",
        3: "PNS",
        4: "Wirausaha",
        5: "Peg. Swasta",
        6: "TNI / POLRI",
        7: "Lainnya",

    }
    return role.get(pa, "unknown")

def convertPenghasilanAyah(pa):
    role = {
        0: "Tidak Berpenghasilan",
        1: "< Rp. 250.000",
        2: "Rp. 250.001 - Rp. 500.000",
        3: "Rp. 500.001 - Rp. 750.000",
        4: "Rp. 750.001 - Rp. 1.000.000",
        5: "Rp. 1.000.001 - Rp. 1.250.000",
        6: "Rp. 1.250.001 - Rp. 1.500.000",
        7: "Rp. 1.500.001 - Rp. 1.750.000",
        8: "Rp. 1.750.001 - Rp. 2.000.000",
        9: "Rp. 2.000.001 - Rp. 2.250.000",
        10: "Rp. 2.250.001 - Rp. 2.500.000",
        11: "Rp. 2.500.001 - Rp. 2.750.000",
        12: "Rp. 2.750.001 - Rp. 3.000.000",
        13: "Rp. 3.000.001 - Rp. 3.250.000",
        14: "Rp. 3.250.001 - Rp. 3.500.000",
        15: "Rp. 3.500.001 - Rp. 3.750.000",
        16: "Rp. 3.750.001 - Rp. 4.000.000",
        17: "Rp. 4.000.001 - Rp. 4.250.000",
        18: "Rp. 4.250.001 - Rp. 4.500.000",
        19: "Rp. 4.500.001 - Rp. 4.750.000",
        20: "Rp. 4.750.001 - Rp. 5.000.000",
        21: "Rp. 5.000.001 - Rp. 5.250.000",
        22: "Rp. 5.250.001 - Rp. 5.500.000",
        23: "Rp. 5.500.001 - Rp. 5.750.000"
    }
    return role.get(pa, "unknown")

def convertStatusAyah(pa):
    role = {
        0: "Wafat",
        1: "Hidup",
        2: "Bercerai"
    }
    return role.get(pa, "unknown")

def convertPekerjaanIbu(pa):
    role = {
        0: "TIDAK BEKERJA",
        1: "Petani",
        2: "Wirausaha",
        3: "Pegawai Swasta",
        4: "PNS",
        5: "Lainnya",
    }
    return role.get(pa, "unknown")

def convertPenghasilanIbu(pa):
    role = {
        0: "Tidak Berpenghasilan",
        1: "< Rp. 250.000",
        2: "Rp. 250.001 - Rp. 500.000",
        3: "Rp. 500.001 - Rp. 750.000",
        4: "Rp. 750.001 - Rp. 1.000.000",
        5: "Rp. 1.000.001 - Rp. 1.250.000",
        6: "Rp. 1.250.001 - Rp. 1.500.000",
        7: "Rp. 1.500.001 - Rp. 1.750.000",
        8: "Rp. 1.750.001 - Rp. 2.000.000",
        9: "Rp. 2.000.001 - Rp. 2.250.000",
        10: "Rp. 2.250.001 - Rp. 2.500.000",
        11: "Rp. 2.500.001 - Rp. 2.750.000",
        12: "Rp. 2.750.001 - Rp. 3.000.000",
        13: "Rp. 3.000.001 - Rp. 3.250.000",
        14: "Rp. 3.250.001 - Rp. 3.500.000",
        15: "Rp. 3.500.001 - Rp. 3.750.000",
        16: "Rp. 3.750.001 - Rp. 4.000.000",
        17: "Rp. 4.000.001 - Rp. 4.250.000",
        18: "Rp. 4.250.001 - Rp. 4.500.000",
        19: "Rp. 4.500.001 - Rp. 4.750.000",
        20: "Rp. 4.750.001 - Rp. 5.000.000",
        21: "Rp. 5.000.001 - Rp. 5.250.000",
        22: "Rp. 5.250.001 - Rp. 5.500.000"
    }
    return role.get(pa, "unknown")

def convertStatusIbu(pa):
    role = {
        0: "Wafat",
        1: "Hidup",
    }
    return role.get(pa, "unknown")

def convertKepemilikanRumah(pa):
    role = {
        0: "Tidak Memiliki",
        1: "Menumpang Tanpa Ijin",
        2: "Menumpang",
        3: "Sewa Bulanan",
        4: "Sewa Tahunan",
        5: "Sendiri"
    }
    return role.get(pa, "unknown")

def convertSumberAir(pa):
    role = {
        0: "Sumur",
        1: "Sungai/Mata Air",
        2: "PDAM",
        3: "Kemasan"
    }
    return role.get(pa, "unknown")

def convertBiayaListrikBulanan(pa):
    role = {
        0: 50000,
        1: 100000,
        2: 150000,
        3: 200000,
        4: 250000,
        5: 300000
    }
    return role.get(pa, "unknown")

def convertKondisiRumah(pa):
    role = {
        0: "Buruk",
        1: "Sedang",
        2: "Baik"
    }
    return role.get(pa, "unknown")

def convertUKT(pa):
    role = {
        0: "Kelompok 1",
        1: "Kelompok 2",
        2: "Kelompok 3",
        3: "Kelompok 4",
        4: "Kelompok 5",
        5: "Kelompok 6",
        6: "Kelompok 7",
        7: "Kelompok 8",
    }
    return role.get(pa, "unknown")

app.jinja_env.globals.update(convertPA=convertPekerjaanAyah,convertPA1=convertPenghasilanAyah,convertSA=convertStatusAyah,convertPI=convertPekerjaanIbu,convertPI1=convertPenghasilanIbu,convertSI=convertStatusIbu,convertKR=convertKepemilikanRumah,convertSA1=convertSumberAir,convertBLB=convertBiayaListrikBulanan,convertKR1=convertKondisiRumah,convertUKT=convertUKT)


@app.route('/')
def index():
    if 'nama' in session:
        try:
            cur = mysql.connection.cursor()
            cur.execute('SELECT COUNT(*) FROM datatesting')
            uji = cur.fetchone()
            cur.execute('SELECT COUNT(*) FROM datatraining')
            latih = cur.fetchone()
            cur.close()
            return render_template('dashboard.html', nama=session['nama'], testing=uji[0], training=latih[0])
        except Exception as e:
            return render_template('login.html')
    else:
        return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        try:
            cur = mysql.connection.cursor()
            cur.execute("SELECT username, nama, password FROM tbl_users WHERE username = %s", (username,))
            user = cur.fetchone()
            cur.close()

            if user and bcrypt.check_password_hash(user[2], password):
                session['nama'] = user[1]
                return redirect(url_for('index'))
            else:
                flash('ERROR: Username dan Password Anda Salah')
                return render_template('login.html')

        except Exception as e:
            flash('ERROR: Username dan Password Anda Salah')
            return render_template('login.html')
    
    return render_template('login.html')
def create_hashed_password(password):
    return bcrypt.generate_password_hash(password).decode('utf-8')

@app.route('/insert', methods=['POST'])
def insert():
    if request.method == "POST":
        flash("Register Berhasil")
        nama = request.form['nama']
        email = request.form['email']
        username = request.form['username']
        password = request.form['password']
        
        hashed_password = create_hashed_password(password)
        
        cur = mysql.connection.cursor()
        cur.execute("INSERT INTO tbl_users (nama, email, username, password) VALUES (%s, %s, %s, %s)", (nama, email, username, hashed_password))
        mysql.connection.commit()
        cur.close()
        return redirect(url_for('user'))
    
@app.route('/delete/<string:id_data>', methods = ['POST','DELETE'])
def delateuser(id_data):
    if (request.form['_method'] == 'DELETE'):
        flash("Delete Data Berhasil")
        cur = mysql.connection.cursor()
        cur.execute("DELETE FROM tbl_users WHERE id = %s", (id_data,))
        mysql.connection.commit()
        cur.close()
        return redirect (url_for('user'))

@app.route('/user/reset/<user_id>', methods=['POST', 'PUT'])
def putUserReset(user_id):
    password = request.form['password']
    password2 = request.form['password2']
    
    if password == password2:
        hashed_password = bcrypt.generate_password_hash(password).decode('utf-8')
        flash("Change Password Berhasil")
        cur = mysql.connection.cursor()
        cur.execute("""UPDATE tbl_users SET password = %s WHERE id = %s""", (hashed_password, user_id))
        mysql.connection.commit()
        cur.close()
        return redirect(url_for('user'))
    else:
        flash("Password tidak cocok")
        return redirect(url_for('user'))

@app.route ('/user')
def user ():
    if 'nama' in session:
        cur = mysql.connection.cursor()
        cur.execute ("SELECT * From tbl_users")
        data =cur.fetchall()
        cur.close()
        return render_template('user.html', tbl_users = data, nama=session['nama'] )
    else:
        return render_template('login.html')
   
@app.route ('/datatraining', methods = ['GET'])
def datatraining ():    
    if 'nama' in session:
        # page = request.args.get('page', default=1, type=int)
        # per_page = 10

        # offset = (page - 1) * per_page

        cur = mysql.connection.cursor()
        # cur.execute('SELECT COUNT(*) FROM datatraining')
        # total = cur.fetchone()[0]

        cur.execute ("SELECT * From datatraining")
        data = cur.fetchall()
        cur.close()

        # pagination = Pagination(
        #     page=page,
        #     total=total,
        #     per_page=per_page,
        #     url='datatraining',
        #     record_name='tbl_datatraining'
        # )
        return render_template('datatraining.html', nama=session['nama'], tbl_datatraining = data)
    else:
        return render_template('login.html')
        
@app.route ('/datatraining', methods = ['POST'])
def postdatatraining ():
    if request.method == 'POST':
        try:
            data = request.files['file']
            data = pd.read_excel(data)

            # Mengganti nilai string kosong ('') dengan NaN
            data.replace('', pd.NA, inplace=True)
            data.replace('-', pd.NA, inplace=True)

            # Menghapus baris dengan nilai kosong atau NaN di salah satu kolom
            data = data.dropna(how='any')

            data['Nilai Pekerjaan Ayah'] = data['Pekerjaan Ayah'].replace(mappingPekerjaanAyah)
            data['Nilai Penghasilan Ayah'] = data['Penghasilan Ayah'].replace(mappingPenghasilanAyah)
            data['Nilai Status Ayah'] = data['Status Ayah'].replace(mappingStatusAyah)
            data['Nilai Pekerjaan Ibu'] = data['Pekerjaan Ibu'].replace(mappingPekerjaanIbu)
            data['Nilai Penghasilan Ibu'] = data['Penghasilan Ibu'].replace(mappingPenghasilanIbu)
            data['Nilai Status Ibu'] = data['Status Ibu'].replace(mappingStatusIbu)
            data['Nilai Jumlah Tanggungan'] = data['Jumlah Tanggungan'].apply(extract_number)
            data['Nilai Kepemilikan Rumah'] = data['Kepemilikan Rumah'].replace(mappingKepemilikanRumah)
            data['Nilai Sumber Air'] = data['Sumber Air'].replace(mappingSumberAir)
            data['Nilai Biaya Listrik Bulanan'] = data['Biaya Listrik Bulanan'].replace(mappingBiayaListrikBulanan)
            data['Nilai Kondisi Rumah'] = data['Kondisi Rumah'].replace(mappingKondisiRumah)
            
            cur = mysql.connection.cursor()
            # Iterasi melalui setiap baris DataFrame dan menyimpan data ke database
            for index, row in data.iterrows():
                # Menjalankan kueri untuk menyimpan data
                cur.execute("INSERT INTO datatraining (nama, pekerjaan_ayah, penghasilan_ayah, status_ayah, pekerjaan_ibu, penghasilan_ibu, status_ibu, jumlah_tanggungan_keluarga, kepemilikan_rumah, sumber_air, kendaraanroda_4, kendaraanroda_2, biaya_listrik, watt_listrik, kondisi_rumah, ukt) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)", 
                            (
                                row['Nama Siswa'], 
                                row['Nilai Pekerjaan Ayah'], 
                                row['Nilai Penghasilan Ayah'], 
                                row['Nilai Status Ayah'], 
                                row['Nilai Pekerjaan Ibu'],
                                row['Nilai Penghasilan Ibu'],
                                row['Nilai Status Ibu'],
                                row['Nilai Jumlah Tanggungan'],
                                row['Nilai Kepemilikan Rumah'],
                                row['Nilai Sumber Air'],
                                row['Kendaraan Roda 4'],
                                row['Kendaraan Roda 2'],
                                row['Nilai Biaya Listrik Bulanan'],
                                row['Watt Listrik'],
                                row['Nilai Kondisi Rumah'],
                                row['kluster']
                                ))
            mysql.connection.commit()
            cur.close()
            flash("Data Training Berhasil DiUpload")
            return redirect(url_for('datatraining'))
        except Exception as e:
            flash("ERROR: Terjadi Kesalahan Saat Menambah Data Training")
            return redirect(url_for('datatraining'))
   
@app.route('/deletedatatraining/<string:id_data>', methods = ['POST','DELETE'])
def deletedatatraining(id_data):
    if (request.form['_method'] == 'DELETE'):
        flash("Delete Data Training Berhasil")
        cur = mysql.connection.cursor()
        cur.execute("DELETE FROM datatraining WHERE id_training = %s", (id_data,))
        mysql.connection.commit()
        cur.close()
        return redirect (url_for('datatraining'))    

@app.route ('/datatesting', methods = ['GET'])
def datatesting():
    if 'nama' in session:
        cur = mysql.connection.cursor()
        cur.execute ("SELECT * From datatesting")
        data =cur.fetchall()
        cur.close()
        return render_template('datatesting.html', nama=session['nama'], tbl_datatesting = data)
    else:
        return render_template('login.html')
    
@app.route ('/datatesting', methods = ['POST'])
def postdatatesting():
    try:
        cur = mysql.connection.cursor()
        cur.execute("SELECT pekerjaan_ayah, penghasilan_ayah, status_ayah, pekerjaan_ibu, penghasilan_ibu, status_ibu, jumlah_tanggungan_keluarga, kepemilikan_rumah, sumber_air, kendaraanroda_4, kendaraanroda_2, biaya_listrik, watt_listrik, kondisi_rumah, ukt FROM datatraining")
        data = cur.fetchall()
        cur.close()

    # Konversi tuple menjadi dictionary dengan menggunakan nama kolom sebagai kunci
    
        dictionary = {
            'pekerjaan_ayah': [subtuple[0] for subtuple in data],
            'penghasilan_ayah': [subtuple[1] for subtuple in data],
            'status_ayah': [subtuple[2] for subtuple in data],
            'pekerjaan_ibu': [subtuple[3] for subtuple in data],
            'penghasilan_ibu': [subtuple[4] for subtuple in data],
            'status_ibu': [subtuple[5] for subtuple in data],
            'jumlah_tanggungan': [subtuple[6] for subtuple in data],
            'kepemilikan_rumah': [subtuple[7] for subtuple in data],
            'sumber_air': [subtuple[8] for subtuple in data],
            'kendaraan_roda_4': [subtuple[9] for subtuple in data],
            'kendaraan_roda_2': [subtuple[10] for subtuple in data],
            'biaya_listrik': [subtuple[11] for subtuple in data],
            'watt_listrik': [subtuple[12] for subtuple in data],
            'kondisi_rumah': [subtuple[13] for subtuple in data],
            'kluster': [subtuple[14] for subtuple in data]
            }
        
        new_data = pd.DataFrame(dictionary)
        X = new_data.drop('kluster', axis=1)
        y = new_data['kluster']

        # Membagi data menjadi data latih dan data uji dengan shuffle=False
        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=None, shuffle=False, random_state=42)

        # Inisialisasi dan melatih model Random Forest
        rf_classifier = RandomForestClassifier(n_estimators=100, random_state=42)
        rf_classifier.fit(X_train, y_train)
    
        if request.form['excel'] == 'True':
            
            data = request.files['file']
            data = pd.read_excel(data)

            data['pekerjaan_ayah'] = data['Pekerjaan Ayah'].replace(mappingPekerjaanAyah)
            data['penghasilan_ayah'] = data['Penghasilan Ayah'].replace(mappingPenghasilanAyah)
            data['status_ayah'] = data['Status Ayah'].replace(mappingStatusAyah)
            data['pekerjaan_ibu'] = data['Pekerjaan Ibu'].replace(mappingPekerjaanIbu)
            data['penghasilan_ibu'] = data['Penghasilan Ibu'].replace(mappingPenghasilanIbu)
            data['status_ibu'] = data['Status Ibu'].replace(mappingStatusIbu)
            data['jumlah_tanggungan'] = data['Jumlah Tanggungan'].apply(extract_number)
            data['kepemilikan_rumah'] = data['Kepemilikan Rumah'].replace(mappingKepemilikanRumah)
            data['sumber_air'] = data['Sumber Air'].replace(mappingSumberAir)
            data['kendaraan_roda_4'] = data['Kendaraan Roda 4']
            data['kendaraan_roda_2'] = data['Kendaraan Roda 2']
            data['biaya_listrik'] = data['Biaya Listrik Bulanan'].replace(mappingBiayaListrikBulanan)
            data['watt_listrik'] = data['Watt Listrik']
            data['kondisi_rumah'] = data['Kondisi Rumah'].replace(mappingKondisiRumah)

            data = data.drop(['Pekerjaan Ayah', 'Penghasilan Ayah', 'Status Ayah', 'Pekerjaan Ibu', 'Penghasilan Ibu', 'Status Ibu', 'Jumlah Tanggungan', 'Kepemilikan Rumah', 'Sumber Air', 'Kendaraan Roda 4', 'Kendaraan Roda 2', 'Biaya Listrik Bulanan', 'Watt Listrik', 'Kondisi Rumah'], axis=1)
            test = data.drop(['Jurusan', 'Nama Siswa', 'Prodi'], axis=1)
            test = pd.DataFrame(test)
            data = pd.DataFrame(data)

            # Prediksi kelas menggunakan model yang telah dilatih
            predicted_class = rf_classifier.predict(test)

            # Dictionary b dengan harga berdasarkan prodi dan ukt
            b = {
            'Administrasi Bisnis': {
            0: '500.000,00', 1: '1.000.000,00', 2: '2.000.000,00', 3: '2.500.000,00', 
            4: '3.000.000,00', 5: '3.750.000,00', 6: '4.500.000,00', 7: '5.500.000,00'
            },
            'Akuntansi': {
                0: '500.000,00', 1: '1.000.000,00', 2: '2.000.000,00', 3: '2.500.000,00', 
                4: '3.000.000,00', 5: '3.750.000,00', 6: '4.500.000,00', 7: '5.500.000,00'
            },
            'Perbankan dan Keuangan': {
                0: '500.000,00', 1: '1.000.000,00', 2: '2.500.000,00', 3: '3.000.000,00', 
                4: '3.500.000,00', 5: '4.250.000,00', 6: '5.000.000,00', 7: '6.000.000,00'
            },
            'Teknologi Elektronika': {
                0: '500.000,00', 1: '1.000.000,00', 2: '2.500.000,00', 3: '3.000.000,00', 
                4: '3.500.000,00', 5: '4.250.000,00', 6: '5.000.000,00', 7: '6.000.000,00'
            },
            'Teknologi Industri': {
                0: '500.000,00', 1: '1.000.000,00', 2: '2.500.000,00', 3: '3.000.000,00', 
                4: '3.500.000,00', 5: '4.250.000,00', 6: '5.000.000,00', 7: '6.000.000,00'
            },
            'Teknologi Kimia': {
                0: '500.000,00', 1: '1.000.000,00', 2: '2.500.000,00', 3: '3.000.000,00', 
                4: '3.500.000,00', 5: '4.250.000,00', 6: '5.000.000,00', 7: '6.000.000,00'
            },
            'Teknologi Kontruksi Bangunan Air': {
                0: '500.000,00', 1: '1.000.000,00', 2: '2.500.000,00', 3: '3.000.000,00', 
                4: '3.500.000,00', 5: '4.250.000,00', 6: '5.000.000,00', 7: '6.000.000,00'
            },
            'Teknologi Kontruksi Bangunan Gedung': {
                0: '500.000,00', 1: '1.000.000,00', 2: '2.500.000,00', 3: '3.000.000,00', 
                4: '3.500.000,00', 5: '4.250.000,00', 6: '5.000.000,00', 7: '6.000.000,00'
            },
            'Teknologi Kontruksi Jalan dan Jembatan': {
                0: '500.000,00', 1: '1.000.000,00', 2: '2.500.000,00', 3: '3.000.000,00', 
                4: '3.500.000,00', 5: '4.250.000,00', 6: '5.000.000,00', 7: '6.000.000,00'
            },
            'Teknologi Listrik': {
                0: '500.000,00', 1: '1.000.000,00', 2: '2.500.000,00', 3: '3.000.000,00', 
                4: '3.500.000,00', 5: '4.250.000,00', 6: '5.000.000,00', 7: '6.000.000,00'
            },
            'Teknologi Mesin': {
                0: '500.000,00', 1: '1.000.000,00', 2: '3.000.000,00', 3: '3.500.000,00', 
                4: '4.250.000,00', 5: '5.000.000,00', 6: '6.000.000,00', 7: '7.000.000,00'
            },
            'Teknologi Pengelohan Minyak dan Gas': {
                0: '500.000,00', 1: '1.000.000,00', 2: '2.500.000,00', 3: '3.000.000,00', 
                4: '3.500.000,00', 5: '4.250.000,00', 6: '5.000.000,00', 7: '6.000.000,00'
            },
            'Teknologi Telekomunikasi': {
                0: '500.000,00', 1: '1.000.000,00', 2: '2.500.000,00', 3: '3.000.000,00', 
                4: '3.500.000,00', 5: '4.250.000,00', 6: '5.000.000,00', 7: '6.000.000,00'
            },
            'Akuntansi Lembaga Keuangan Syariah': {
                0: '500.000,00', 1: '1.000.000,00', 2: '3.000.000,00', 3: '3.500.000,00', 
                4: '4.250.000,00', 5: '5.000.000,00', 6: '6.000.000,00', 7: '7.000.000,00'
            },
            'Teknik Informatika': {
                0: '500.000,00', 1: '1.000.000,00', 2: '3.000.000,00', 3: '3.500.000,00', 
                4: '4.250.000,00', 5: '5.000.000,00', 6: '6.000.000,00', 7: '7.000.000,00'
            },
            'Teknologi Rekayasa Instrumentasi dan Kontrol': {
                0: '500.000,00', 1: '1.000.000,00', 2: '3.000.000,00', 3: '3.500.000,00', 
                4: '4.250.000,00', 5: '5.000.000,00', 6: '6.000.000,00', 7: '7.000.000,00'
            },
            'Teknologi Rekayasa Jaringan Telekomunikasi': {
                0: '500.000,00', 1: '1.000.000,00', 2: '3.000.000,00', 3: '3.500.000,00', 
                4: '4.250.000,00', 5: '5.000.000,00', 6: '6.000.000,00', 7: '7.000.000,00'
            },
            'Teknologi Rekayasa Kimia Industri': {
                0: '500.000,00', 1: '1.000.000,00', 2: '3.000.000,00', 3: '3.500.000,00', 
                4: '4.250.000,00', 5: '5.000.000,00', 6: '6.000.000,00', 7: '7.000.000,00'
            },
            'Teknologi Rekayasa Komputer Jaringan': {
                0: '500.000,00', 1: '1.000.000,00', 2: '3.000.000,00', 3: '3.500.000,00', 
                4: '4.250.000,00', 5: '5.000.000,00', 6: '6.000.000,00', 7: '7.000.000,00'
            },
            'Teknologi Rekayasa Konstruksi Jalan dan Jembatan': {
                0: '500.000,00', 1: '1.000.000,00', 2: '3.000.000,00', 3: '3.500.000,00', 
                4: '4.250.000,00', 5: '5.000.000,00', 6: '6.000.000,00', 7: '7.000.000,00'
            },
            'Teknologi Rekayasa Manufaktur': {
                0: '500.000,00', 1: '1.000.000,00', 2: '3.000.000,00', 3: '3.500.000,00', 
                4: '4.250.000,00', 5: '5.000.000,00', 6: '6.000.000,00', 7: '7.000.000,00'
            },
            'Teknologi Rekayasa Pembangkit Energi': {
                0: '500.000,00', 1: '1.000.000,00', 2: '3.000.000,00', 3: '3.500.000,00', 
                4: '4.250.000,00', 5: '5.000.000,00', 6: '6.000.000,00', 7: '7.000.000,00'
            }
                }

            data['Ukt'] = predicted_class

            # Fungsi untuk mendapatkan harga berdasarkan prodi dan ukt
            def get_harga(row, data_b):
                prodi = row['Prodi']
                ukt_level = row['Ukt']
                return data_b.get(prodi, {}).get(ukt_level, None)
        
            # Terapkan fungsi ke DataFrame untuk membuat kolom 'harga'
            data['harga'] = data.apply(get_harga, axis=1, data_b=b)
            data = pd.DataFrame(data)
            print(data)            
            cur = mysql.connection.cursor()
            # Iterasi melalui setiap baris DataFrame dan menyimpan data ke database
            for index, row in data.iterrows():
                # Menjalankan kueri untuk menyimpan data
                cur.execute("INSERT INTO datatesting (nama, jurusan, prodi, pekerjaan_ayah, penghasilan_ayah, status_ayah, pekerjaan_ibu, penghasilan_ibu, status_ibu, jumlah_tanggungan_keluarga, kepemilikan_rumah, sumber_air, kendaraanroda_4, kendaraanroda_2, biaya_listrik, watt_listrik, kondisi_rumah, ukt, harga) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)", 
                            (
                                row['Nama Siswa'],
                                row['Jurusan'],
                                row['Prodi'], 
                                row['pekerjaan_ayah'], 
                                row['penghasilan_ayah'], 
                                row['status_ayah'], 
                                row['pekerjaan_ibu'],
                                row['penghasilan_ibu'],
                                row['status_ibu'],
                                row['jumlah_tanggungan'],
                                row['kepemilikan_rumah'],
                                row['sumber_air'],
                                row['kendaraan_roda_4'],
                                row['kendaraan_roda_2'],
                                row['biaya_listrik'],
                                row['watt_listrik'],
                                row['kondisi_rumah'],
                                row['Ukt'],
                                row['harga']
                                ))
            mysql.connection.commit()
            cur.close()

        else:
            nama = request.form['nama']
            jurusan = request.form['jurusan']
            prodi = request.form['prodi']
            pekerjaan_ayah = int(request.form['pekerjaan_ayah'])
            penghasilan_ayah = int(request.form['penghasilan_ayah'])
            status_ayah = int(request.form['status_ayah'])
            pekerjaan_ibu = int(request.form['pekerjaan_ibu'])
            penghasilan_ibu = int(request.form['penghasilan_ibu'])
            status_ibu = int(request.form['status_ibu'])
            jumlah_tanggungan = int(request.form['jumlah_tanggungan'])
            kepemilikan_rumah = int(request.form['kepemilikan_rumah'])
            sumber_air = int(request.form['sumber_air'])
            kendaraan_roda_4 = int(request.form['kendaraan_roda_4'])
            kendaraan_roda_2 = int(request.form['kendaraan_roda_2'])
            biaya_listrik = int(request.form['biaya_listrik'])
            watt_listrik = int(request.form['watt_listrik'])
            kondisi_rumah = int(request.form['kondisi_rumah'])

        new_data1 = {
            'nama': [nama],
            'jurusan': [jurusan],
            'prodi': [prodi],
            'pekerjaan_ayah': [pekerjaan_ayah],
            'penghasilan_ayah': [penghasilan_ayah],
            'status_ayah' : [status_ayah],
            'pekerjaan_ibu': [pekerjaan_ibu],
            'penghasilan_ibu': [penghasilan_ibu],
            'status_ibu' : [status_ibu],
            'jumlah_tanggungan': [jumlah_tanggungan],
            'kepemilikan_rumah': [kepemilikan_rumah],
            'sumber_air' : [sumber_air],
            'kendaraan_roda_4' : [kendaraan_roda_4],
            'kendaraan_roda_2' : [kendaraan_roda_2],
            'biaya_listrik' : [biaya_listrik],
            'watt_listrik' :[watt_listrik],
            'kondisi_rumah' : [kondisi_rumah]
        }

        df_new = pd.DataFrame(new_data1)
        df = df_new.drop(['nama', 'prodi', 'jurusan'], axis=1)
        # Prediksi kelas menggunakan model yang telah dilatih
        predicted_class = rf_classifier.predict(df)

        df_new['ukt'] = predicted_class
        
        # Dictionary b dengan harga berdasarkan prodi dan ukt
        b = {
            'Administrasi Bisnis': {
        0: '500.000,00', 1: '1.000.000,00', 2: '2.000.000,00', 3: '2.500.000,00', 
        4: '3.000.000,00', 5: '3.750.000,00', 6: '4.500.000,00', 7: '5.500.000,00'
        },
        'Akuntansi': {
            0: '500.000,00', 1: '1.000.000,00', 2: '2.000.000,00', 3: '2.500.000,00', 
            4: '3.000.000,00', 5: '3.750.000,00', 6: '4.500.000,00', 7: '5.500.000,00'
        },
        'Perbankan dan Keuangan': {
            0: '500.000,00', 1: '1.000.000,00', 2: '2.500.000,00', 3: '3.000.000,00', 
            4: '3.500.000,00', 5: '4.250.000,00', 6: '5.000.000,00', 7: '6.000.000,00'
        },
        'Teknologi Elektronika': {
            0: '500.000,00', 1: '1.000.000,00', 2: '2.500.000,00', 3: '3.000.000,00', 
            4: '3.500.000,00', 5: '4.250.000,00', 6: '5.000.000,00', 7: '6.000.000,00'
        },
        'Teknologi Industri': {
            0: '500.000,00', 1: '1.000.000,00', 2: '2.500.000,00', 3: '3.000.000,00', 
            4: '3.500.000,00', 5: '4.250.000,00', 6: '5.000.000,00', 7: '6.000.000,00'
        },
        'Teknologi Kimia': {
            0: '500.000,00', 1: '1.000.000,00', 2: '2.500.000,00', 3: '3.000.000,00', 
            4: '3.500.000,00', 5: '4.250.000,00', 6: '5.000.000,00', 7: '6.000.000,00'
        },
        'Teknologi Kontruksi Bangunan Air': {
            0: '500.000,00', 1: '1.000.000,00', 2: '2.500.000,00', 3: '3.000.000,00', 
            4: '3.500.000,00', 5: '4.250.000,00', 6: '5.000.000,00', 7: '6.000.000,00'
        },
        'Teknologi Kontruksi Bangunan Gedung': {
            0: '500.000,00', 1: '1.000.000,00', 2: '2.500.000,00', 3: '3.000.000,00', 
            4: '3.500.000,00', 5: '4.250.000,00', 6: '5.000.000,00', 7: '6.000.000,00'
        },
        'Teknologi Kontruksi Jalan dan Jembatan': {
            0: '500.000,00', 1: '1.000.000,00', 2: '2.500.000,00', 3: '3.000.000,00', 
            4: '3.500.000,00', 5: '4.250.000,00', 6: '5.000.000,00', 7: '6.000.000,00'
        },
        'Teknologi Listrik': {
            0: '500.000,00', 1: '1.000.000,00', 2: '2.500.000,00', 3: '3.000.000,00', 
            4: '3.500.000,00', 5: '4.250.000,00', 6: '5.000.000,00', 7: '6.000.000,00'
        },
        'Teknologi Mesin': {
            0: '500.000,00', 1: '1.000.000,00', 2: '3.000.000,00', 3: '3.500.000,00', 
            4: '4.250.000,00', 5: '5.000.000,00', 6: '6.000.000,00', 7: '7.000.000,00'
        },
        'Teknologi Pengelohan Minyak dan Gas': {
            0: '500.000,00', 1: '1.000.000,00', 2: '2.500.000,00', 3: '3.000.000,00', 
            4: '3.500.000,00', 5: '4.250.000,00', 6: '5.000.000,00', 7: '6.000.000,00'
        },
        'Teknologi Telekomunikasi': {
            0: '500.000,00', 1: '1.000.000,00', 2: '2.500.000,00', 3: '3.000.000,00', 
            4: '3.500.000,00', 5: '4.250.000,00', 6: '5.000.000,00', 7: '6.000.000,00'
        },
        'Akuntansi Lembaga Keuangan Syariah': {
            0: '500.000,00', 1: '1.000.000,00', 2: '3.000.000,00', 3: '3.500.000,00', 
            4: '4.250.000,00', 5: '5.000.000,00', 6: '6.000.000,00', 7: '7.000.000,00'
        },
        'Teknik Informatika': {
            0: '500.000,00', 1: '1.000.000,00', 2: '3.000.000,00', 3: '3.500.000,00', 
            4: '4.250.000,00', 5: '5.000.000,00', 6: '6.000.000,00', 7: '7.000.000,00'
        },
        'Teknologi Rekayasa Instrumentasi dan Kontrol': {
            0: '500.000,00', 1: '1.000.000,00', 2: '3.000.000,00', 3: '3.500.000,00', 
            4: '4.250.000,00', 5: '5.000.000,00', 6: '6.000.000,00', 7: '7.000.000,00'
        },
        'Teknologi Rekayasa Jaringan Telekomunikasi': {
            0: '500.000,00', 1: '1.000.000,00', 2: '3.000.000,00', 3: '3.500.000,00', 
            4: '4.250.000,00', 5: '5.000.000,00', 6: '6.000.000,00', 7: '7.000.000,00'
        },
        'Teknologi Rekayasa Kimia Industri': {
            0: '500.000,00', 1: '1.000.000,00', 2: '3.000.000,00', 3: '3.500.000,00', 
            4: '4.250.000,00', 5: '5.000.000,00', 6: '6.000.000,00', 7: '7.000.000,00'
        },
        'Teknologi Rekayasa Komputer Jaringan': {
            0: '500.000,00', 1: '1.000.000,00', 2: '3.000.000,00', 3: '3.500.000,00', 
            4: '4.250.000,00', 5: '5.000.000,00', 6: '6.000.000,00', 7: '7.000.000,00'
        },
        'Teknologi Rekayasa Konstruksi Jalan dan Jembatan': {
            0: '500.000,00', 1: '1.000.000,00', 2: '3.000.000,00', 3: '3.500.000,00', 
            4: '4.250.000,00', 5: '5.000.000,00', 6: '6.000.000,00', 7: '7.000.000,00'
        },
        'Teknologi Rekayasa Manufaktur': {
            0: '500.000,00', 1: '1.000.000,00', 2: '3.000.000,00', 3: '3.500.000,00', 
            4: '4.250.000,00', 5: '5.000.000,00', 6: '6.000.000,00', 7: '7.000.000,00'
        },
        'Teknologi Rekayasa Pembangkit Energi': {
            0: '500.000,00', 1: '1.000.000,00', 2: '3.000.000,00', 3: '3.500.000,00', 
            4: '4.250.000,00', 5: '5.000.000,00', 6: '6.000.000,00', 7: '7.000.000,00'
        }
            }

        # Fungsi untuk mendapatkan harga berdasarkan prodi dan ukt
        def get_harga(row, data_b):
            prodi = row['prodi']
            ukt_level = row['ukt']
            return data_b.get(prodi, {}).get(ukt_level, None)

        # Terapkan fungsi ke DataFrame untuk membuat kolom 'harga'
        df_new['harga'] = df_new.apply(get_harga, axis=1, data_b=b)

        cur = mysql.connection.cursor()
        cur.execute ("INSERT into datatesting (nama, jurusan, prodi, pekerjaan_ayah, penghasilan_ayah, status_ayah, pekerjaan_ibu, penghasilan_ibu, status_ibu, jumlah_tanggungan_keluarga, kepemilikan_rumah, sumber_air, kendaraanroda_4, kendaraanroda_2, biaya_listrik, watt_listrik, kondisi_rumah, ukt, harga) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)", ( 
            df_new['nama'][0], 
            df_new['jurusan'][0], 
            df_new['prodi'][0], 
            df_new['pekerjaan_ayah'][0], 
            df_new['penghasilan_ayah'][0], 
            df_new['status_ayah'][0], 
            df_new['pekerjaan_ibu'][0],
            df_new['penghasilan_ibu'][0],
            df_new['status_ibu'][0],
            df_new['jumlah_tanggungan'][0],
            df_new['kepemilikan_rumah'][0],
            df_new['sumber_air'][0],
            df_new['kendaraan_roda_4'][0],
            df_new['kendaraan_roda_2'][0],
            df_new['biaya_listrik'][0],
            df_new['watt_listrik'][0],
            df_new['kondisi_rumah'][0],
            df_new['ukt'][0],
            df_new['harga'][0]
            ))
        mysql.connection.commit()
        flash("Data Testing Berhasil Di Tambah")
        return redirect(url_for('datatesting'))
    except Exception as e:
        print("Error:", e) 
        flash(f"ERROR: Terjadi Kesalahan Saat Menambahkan Data Testing {e}")
        # Redirect atau kembalikan sesuai kebutuhan aplikasi Anda
        return redirect(url_for('datatesting'))

@app.route('/deletedatatesting/<string:id_data>', methods = ['POST','DELETE'])
def delatedatatesting(id_data):
    if (request.form['_method'] == 'DELETE'):
        flash("Delete Data Testing Berhasil")
        cur = mysql.connection.cursor()
        cur.execute("DELETE FROM datatesting WHERE id_datatesting = %s", (id_data,))
        mysql.connection.commit()
        cur.close()
        return redirect (url_for('datatesting'))

@app.route ('/dataklasifikasi')
def dataklasifikasi ():
    if 'nama' in session:
        cur = mysql.connection.cursor()
        cur.execute ("SELECT * From datatesting")
        data =cur.fetchall()
        cur.close()
        return render_template('dataklasifikasi.html', nama=session['nama'], tbl_datatesting = data)
    else:
        return render_template('login.html')

@app.route('/logout')
def logout():
    if 'nama' in session:
        session.pop('nama', None)
    return redirect('/login')

if __name__ == "__main__":
    app.run(debug=True)