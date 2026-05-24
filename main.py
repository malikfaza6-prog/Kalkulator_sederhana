from flask import Flask, render_template, request, jsonify
import math

# Konfigurasi Flask - folder template 'tamplates' sesuai struktur folder proyek Anda
app = Flask(__name__, template_folder='tamplates', static_folder='tamplates', static_url_path='/static')

# ─────────────────────────────────────────────────────────
#  ROUTING HALAMAN (Render HTML)
# ─────────────────────────────────────────────────────────

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/logika.html')
def logika():
    return render_template('logika.html')

@app.route('/mata_uang.html')
def mata_uang():
    return render_template('mata_uang.html')

@app.route('/suhu.html')
def suhu():
    return render_template('suhu.html')

@app.route('/fakbonaci.html')
def fakbonaci():
    return render_template('fakbonaci.html')


# ─────────────────────────────────────────────────────────
#  ENDPOINT API UTAMA  →  POST /api/kalkulator
#  Body JSON: { "mode": "...", ...parameter lain... }
# ─────────────────────────────────────────────────────────

@app.route('/api/kalkulator', methods=['POST'])
def kalkulator():
    data = request.get_json()
    if not data:
        return jsonify({'error': 'Data JSON tidak ditemukan'}), 400

    mode = data.get('mode', '')

    if mode == 'aritmatika':
        return hitung_aritmatika(data)
    elif mode == 'logika':
        return hitung_logika(data)
    elif mode == 'mata_uang':
        return hitung_mata_uang(data)
    elif mode == 'suhu':
        return hitung_suhu(data)
    elif mode == 'fibonacci':
        return hitung_fibonacci(data)
    elif mode == 'faktorial':
        return hitung_faktorial(data)
    else:
        return jsonify({'error': f'Mode tidak dikenali: {mode}'}), 400


# ─────────────────────────────────────────────────────────
#  1. ARITMATIKA  (termasuk SIN / COS dalam derajat)
# ─────────────────────────────────────────────────────────

def hitung_aritmatika(data):
    """
    Input  : { "mode": "aritmatika", "expression": "sin(90)+cos(0)*2" }
    Output : { "result": "3" }
    """
    try:
        expression = data.get('expression', '').strip()
        if not expression:
            return jsonify({'result': 'Error: ekspresi kosong'})

        # Namespace aman – sin/cos menerima derajat
        safe_ns = {
            'sin': lambda x: round(math.sin(math.radians(x)), 10),
            'cos': lambda x: round(math.cos(math.radians(x)), 10),
            '__builtins__': {}
        }

        result = eval(expression, safe_ns)

        # Rapikan desimal
        if isinstance(result, float):
            result = round(result, 10)
            if result == int(result):
                result = int(result)

        return jsonify({'result': str(result)})

    except ZeroDivisionError:
        return jsonify({'result': 'Error: bagi nol'})
    except Exception:
        return jsonify({'result': 'Error'})


# ─────────────────────────────────────────────────────────
#  2. LOGIKA  (Gerbang Logika / Bitwise)
# ─────────────────────────────────────────────────────────

def hitung_logika(data):
    """
    Input  : { "mode": "logika", "operasi": "AND", "a": 5, "b": 3 }
    Output : { "result": 1, "biner_a": "0b101", "biner_b": "0b11", "biner_result": "0b1" }
    Operasi: AND, OR, XOR, NOT, NAND, NOR, XNOR
    """
    try:
        operasi = data.get('operasi', '').upper()
        a = int(data.get('a', 0))
        b = int(data.get('b', 0))

        if operasi == 'AND':
            result = a & b
        elif operasi == 'OR':
            result = a | b
        elif operasi == 'XOR':
            result = a ^ b
        elif operasi == 'NOT':
            result = ~a
        elif operasi == 'NAND':
            result = ~(a & b)
        elif operasi == 'NOR':
            result = ~(a | b)
        elif operasi == 'XNOR':
            result = ~(a ^ b)
        else:
            return jsonify({'error': f'Operasi tidak dikenal: {operasi}'}), 400

        return jsonify({
            'result': result,
            'operasi': operasi,
            'a': a,
            'b': b,
            'biner_a': bin(a),
            'biner_b': bin(b) if operasi != 'NOT' else '-',
            'biner_result': bin(result)
        })

    except Exception as e:
        return jsonify({'error': str(e)}), 400


# ─────────────────────────────────────────────────────────
#  3. MATA UANG  (Konversi ke semua valuta sekaligus)
# ─────────────────────────────────────────────────────────

# Kurs statis – 1 satuan valuta = X IDR
KURS = {
    'IDR': 1,
    'USD': 16300,
    'EUR': 17800,
    'SGD': 12100,
    'JPY': 109,
    'MYR': 3500,
    'GBP': 20700,
    'AUD': 10500,
}

def hitung_mata_uang(data):
    """
    Input  : { "mode": "mata_uang", "dari": "USD", "jumlah": 10 }
    Output : { "hasil": { "IDR": "163,000", "EUR": "9.1573", ... } }
    """
    try:
        dari = data.get('dari', 'IDR').upper()
        jumlah = float(data.get('jumlah', 0))

        if dari not in KURS:
            return jsonify({'error': f'Mata uang tidak dikenal: {dari}'}), 400

        nilai_idr = jumlah * KURS[dari]

        hasil = {}
        for kode, rate in KURS.items():
            nilai = nilai_idr / rate
            if kode == 'IDR':
                hasil[kode] = f"{nilai:,.0f}"
            elif kode == 'JPY':
                hasil[kode] = f"{nilai:,.2f}"
            else:
                hasil[kode] = f"{nilai:,.4f}"

        return jsonify({'dari': dari, 'jumlah': jumlah, 'hasil': hasil})

    except Exception as e:
        return jsonify({'error': str(e)}), 400


# ─────────────────────────────────────────────────────────
#  4. SUHU  (Konversi ke semua satuan sekaligus)
# ─────────────────────────────────────────────────────────

def hitung_suhu(data):
    """
    Input  : { "mode": "suhu", "dari": "C", "nilai": 100 }
    Output : { "hasil": { "C": 100, "F": 212, "K": 373.15, "R": 80 } }
    Satuan : C, F, K, R
    """
    try:
        dari = data.get('dari', 'C').upper()
        nilai = float(data.get('nilai', 0))

        # Pivot ke Celsius
        if dari == 'C':
            c = nilai
        elif dari == 'F':
            c = (nilai - 32) * 5 / 9
        elif dari == 'K':
            c = nilai - 273.15
        elif dari == 'R':
            c = nilai * 5 / 4
        else:
            return jsonify({'error': f'Satuan tidak dikenal: {dari}'}), 400

        hasil = {
            'C': round(c, 4),
            'F': round(c * 9 / 5 + 32, 4),
            'K': round(c + 273.15, 4),
            'R': round(c * 4 / 5, 4),
        }

        return jsonify({'dari': dari, 'nilai': nilai, 'hasil': hasil})

    except Exception as e:
        return jsonify({'error': str(e)}), 400


# ─────────────────────────────────────────────────────────
#  5. FIBONACCI
# ─────────────────────────────────────────────────────────

def hitung_fibonacci(data):
    """
    Input  : { "mode": "fibonacci", "n": 10 }
    Output : { "n": 10, "fibonacci_ke_n": 55, "deret": [0,1,1,...,55] }
    """
    try:
        n = int(data.get('n', 0))

        if n < 0:
            return jsonify({'error': 'Input harus bilangan bulat positif'}), 400
        if n > 50:
            return jsonify({'error': 'Input terlalu besar (maks 50)'}), 400

        deret = []
        a, b = 0, 1
        for _ in range(n + 1):
            deret.append(a)
            a, b = b, a + b

        return jsonify({
            'n': n,
            'fibonacci_ke_n': deret[n],
            'deret': deret
        })

    except Exception as e:
        return jsonify({'error': str(e)}), 400


# ─────────────────────────────────────────────────────────
#  6. FAKTORIAL
# ─────────────────────────────────────────────────────────

def hitung_faktorial(data):
    """
    Input  : { "mode": "faktorial", "n": 7 }
    Output : { "n": 7, "hasil": 5040, "notasi": "7! = 5040" }
    """
    try:
        n = int(data.get('n', 0))

        if n < 0:
            return jsonify({'error': 'Input harus bilangan bulat positif'}), 400
        if n > 170:
            return jsonify({'error': 'Input terlalu besar (maks 170)'}), 400

        result = math.factorial(n)

        return jsonify({
            'n': n,
            'hasil': result,
            'notasi': f"{n}! = {result}"
        })

    except Exception as e:
        return jsonify({'error': str(e)}), 400


# ─────────────────────────────────────────────────────────
#  JALANKAN APLIKASI
# ─────────────────────────────────────────────────────────

if __name__ == '__main__':
    app.run(debug=True)