from flag import Mods

use_mods = 16 # DT
diff_mods = Mods.Easy | Mods.HalfTime | Mods.HardRock | Mods.DoubleTime | Mods.Nightcore

if Mods(use_mods) in diff_mods:
    request_mods = use_mods
else : 
    request_mods = 0


print(diff_mods.value, diff_mods)
print(diff_mods)
print(use_mods, Mods(use_mods))
print(request_mods, Mods(request_mods))


