from flask import Flask, render_template, request, jsonify
import math

# FIX 1: Konfigurasi folder template 'tamplates' dan static 'static' sesuai struktur asli proyek Anda
app = Flask(__name__, template_folder='tamplates', static_folder='static')

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
# ─────────────────────────────────────────────────────────

@app.route('/api/kalkulator', methods=['POST'])
def kalkulator():
    data = request.get_json()
    if not data:
        return jsonify({'error': 'Data JSON tidak ditemukan'}), 400

    # FIX 2: Mendukung pembacaan key 'fitur' dari JavaScript atau 'mode'
    mode = data.get('fitur' if 'fitur' in data else 'mode', '')

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
        return jsonify({'error': f'Mode/Fitur tidak dikenali: {mode}'}), 400


# ─────────────────────────────────────────────────────────
#  1. ARITMATIKA  (termasuk SIN / COS dalam derajat)
# ─────────────────────────────────────────────────────────

def hitung_aritmatika(data):
    try:
        expression = data.get('expression', '').strip()
        if not expression:
            return jsonify({'result': 'Error: ekspresi kosong'})

        safe_ns = {
            'sin': lambda x: round(math.sin(math.radians(x)), 10),
            'cos': lambda x: round(math.cos(math.radians(x)), 10),
            '__builtins__': {}
        }

        result = eval(expression, safe_ns)

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
#  3. MATA UANG 
# ─────────────────────────────────────────────────────────

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
    try:
        # 1. Baca mata uang asal (misal: IDR, USD, EUR) dari JavaScript
        dari = data.get('dari', 'IDR').upper()
        
        # 2. Mengakomodasi jika javascript mengirim parameter 'nilai' atau 'jumlah'
        jumlah = float(data.get('jumlah' if 'jumlah' in data else 'nilai', 0))

        # Cek apakah mata uang asal terdaftar di data KURS
        if dari not in KURS:
            return jsonify({'error': f'Mata uang asal ({dari}) tidak didukung'}), 400

        # 3. RUMUS UTAMA: Konversi nominal ke Rupiah (IDR) sebagai dasar/pivot dasar
        nilai_idr = jumlah * KURS[dari]

        # 4. MODIFIKASI UTAMA: Hitung hasil ke SEMUA mata uang sekaligus untuk tabel bawaan
        hasil = {}
        for kode, rate in KURS.items():
            nilai_konversi = nilai_idr / rate
            
            # Format desimal sesuai jenis mata uangnya
            if kode == 'IDR':
                hasil[kode] = f"{nilai_konversi:,.0f}"
            elif kode == 'JPY':
                hasil[kode] = f"{nilai_konversi:,.2f}"
            else:
                hasil[kode] = f"{nilai_konversi:,.4f}"

        # 5. Kembalikan data dalam bentuk dictionary 'hasil' agar dibaca mulus oleh loop JavaScript kamu
        return jsonify({
            'dari': dari, 
            'jumlah': jumlah, 
            'hasil': hasil
        })

    except Exception as e:
        return jsonify({'error': str(e)}), 400

    @app.route('/api/kalkulator', methods=['POST'])
    def api_kalkulator():
        data = request.get_json()
        if data and data.get('mode') == 'mata_uang':
            # Fungsi hitung_mata_uang sekarang bisa melihat KURS karena KURS ada di atasnya
            return hitung_mata_uang(data)
        return jsonify({'error': 'Mode tidak dikenali'}), 400
# ─────────────────────────────────────────────────────────
#  4. SUHU
# ─────────────────────────────────────────────────────────

def hitung_suhu(data):
    try:
        dari = data.get('dari', 'C').upper()
        nilai = float(data.get('nilai', 0))

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


if __name__ == '__main__':
    app.run(debug=True)