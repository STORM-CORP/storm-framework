# Ini import yang di gunakan
from lib.roar.plugins import register as app


def example():
    # Ini untuk mangambil nama plugin yang ingin di gunakan.
    example = app.plugins.get("storm")

    # Ini untuk mengambil nama fungsi secara spesifik.
    example.plugins.storm_fucn("input user")
    # Atau
    example.plugins.storm_fucn(storm)

    # Ini langsung memasukkan string untuk plugin
    # tanpa tau function plugin.
    # tapi agak lambat karena harus melakukan pencarian otomatis di sisi mesin.
    example.plugins.function("input user")
    # Atau
    example.plugins.function(storm)

    app.plugins.broadcast("saat_masukan_pengguna_diterima", payload="input user")
