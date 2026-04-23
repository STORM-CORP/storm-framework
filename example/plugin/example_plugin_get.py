# Ini import yang di gunakan
from lib.roar.plugin.manager import registry as plugin


def example():
    # Ini untuk mangambil nama plugin yang ingin di gunakan.
    example = plugin.get("storm")

    # Ini untuk mengambil nama fungsi secara spesifik.
    example.plugin.storm_fucn("input user")

    # Ini langsung memasukkan string untuk plugin
    # tanpa tau function plugin.
    # tapi agak lambat karena harus melakukan pencarian otomatis di sisi mesin.
    example.function("input user")
