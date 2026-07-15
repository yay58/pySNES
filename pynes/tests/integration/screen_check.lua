-- Screen check for pyNES integration tests.
-- Waits for the ROM to render, then samples the emulator framebuffer
-- and reports lit (bright) pixels in a given region to RESULT_FILE.
-- Region and output are passed via environment variables.

-- REGIONS format: 'x1,y1,x2,y2;x1,y1,x2,y2;...'
local result_path = os.getenv('RESULT_FILE') or 'screen_result.txt'
local regions = os.getenv('REGIONS') or '0,0,255,239'
local frames = tonumber(os.getenv('WAIT_FRAMES') or 120)
-- HOLD_BUTTONS format: 'right,A' (held on joypad 1 every frame)
local hold = os.getenv('HOLD_BUTTONS') or ''

local buttons = {}
for button in string.gmatch(hold, '[^,]+') do
    buttons[button] = true
end

for _ = 1, frames do
    joypad.set(1, buttons)
    emu.frameadvance()
end

local function count_lit(x1, y1, x2, y2)
    local lit = 0
    for x = x1, x2 do
        for y = y1, y2 do
            local r, g, b = emu.getscreenpixel(x, y, true)
            if r > 128 and g > 128 and b > 128 then
                lit = lit + 1
            end
        end
    end
    return lit
end

local counts = {}
for region in string.gmatch(regions, '[^;]+') do
    local coords = {}
    for value in string.gmatch(region, '[^,]+') do
        table.insert(coords, tonumber(value))
    end
    table.insert(
        counts, count_lit(coords[1], coords[2], coords[3], coords[4])
    )
end

-- sample a background pixel far away from the text
local br, bg, bb = emu.getscreenpixel(8, 8, true)

local f = io.open(result_path, 'w')
f:write('lit=' .. table.concat(counts, ';') .. '\n')
f:write(string.format('bg=%d,%d,%d\n', br, bg, bb))
f:close()

emu.exit()
