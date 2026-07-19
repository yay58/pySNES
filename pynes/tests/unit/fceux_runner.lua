-- FCEUX Headless Runner Server Bridge with On-Screen Terminal Logger
local socket = require("socket")

local host = "127.0.0.1"
local port = 8888

local lines_log = {}
local MAX_LINES = 9
local LINE_HEIGHT = 10

local function screen_log(message)
    print(message)
    table.insert(lines_log, message)
    if #lines_log > MAX_LINES then
        table.remove(lines_log, 1)
    end
    emu.frameadvance()
end

local function draw_terminal_overlay()
    local start_x = 10
    local start_y = 15
    
    for i, line in ipairs(lines_log) do
        gui.text(start_x, start_y + ((i - 1) * LINE_HEIGHT), line, "green", "black")
    end
end

gui.register(draw_terminal_overlay)

-- Bind socket to port and start listening
local server = assert(socket.bind(host, port))
server:settimeout(5.0)

screen_log("[LUA SERVER] Awaiting Python client on port " .. port .. "...")
local client, err = server:accept()

if err or not client then
    screen_log("[LUA SERVER] Connection timeout or failure: " .. tostring(err))
    os.exit()
end

screen_log("[LUA SERVER] Connected to Python Test Harness.")
client:settimeout(nil) -- Switch to standard blocking mode for synchronized testing

local function get_pc()
    return memory.getregister("pc")
end

-- Simulates your Python _run() logic inside the emulator core
local function run_until_idle(max_frames)
    local last_pc = -1
    max_frames = 160
    for frame = 1, max_frames do
        emu.frameadvance()

        local current_pc = get_pc()
        
        if current_pc == last_pc then
            screen_log("[RUN_IDLE] CPU parked at PC=" .. string.format("0x%04X", current_pc) .. " after " .. frame .. " frames")
            return true
        end
        
        last_pc = current_pc
    end
    screen_log("[RUN_IDLE] Timeout after " .. max_frames .. " frames")
    return false
end


-- Main protocol server loop
while true do
    local line, err = client:receive("*l")
    if err then break end
    
    if line:sub(1, 5) == "LOAD:" then
        local size = tonumber(line:sub(6))
        local rom_data = client:receive(size)
        
        screen_log("[LOAD] Received new ROM binary block (" .. size .. " bytes)")
        
        local tmp_path = "tmp_runner_test.nes"
        local f = io.open(tmp_path, "wb")
        f:write(rom_data)
        f:close()
        
        emu.loadrom(tmp_path)
        client:send("ACK\n")
        screen_log("[LOAD] ROM flashed. Emulator Hard Reset.")
        
    elseif line == "RUN_IDLE" then
        screen_log("[EXEC] Running CPU until JMP-to-self idle...")
        local success = run_until_idle(100000)
        if success then
            client:send("OK\n")
            screen_log("[EXEC] CPU parked successfully.")
        else
            client:send("RUNAWAY\n")
            screen_log("[WARN] Runaway execution detected!")
        end
        
    elseif line:sub(1, 4) == "NMI:" then
        local nmi_vector = tonumber(line:sub(5))
        screen_log(string.format("[NMI] Forcing NMI trigger vector: $X", nmi_vector))
        
        local pc = get_pc()
        local status = memory.getregister("p")
        local s = memory.getregister("s")
        
        local pc_high = bit.band(bit.rshift(pc, 8), 0xFF)
        local pc_low  = bit.band(pc, 0xFF)

        memory.writebyte(0x0100 + s, pc_high)
        memory.writebyte(0x0100 + (s - 1), pc_low)
        memory.writebyte(0x0100 + (s - 2), status)
        memory.setregister("s", s - 3)
        memory.setregister("pc", nmi_vector)
        
        local success = run_until_idle(100000)
        if success then
            client:send("OK\n")
        else
            client:send("RUNAWAY\n")
        end
        
    elseif line:sub(1, 5) == "READ:" then
        local addr = tonumber(line:sub(6))
        local val = memory.readbyte(addr)
        client:send(string.char(val))

    elseif line:sub(1, 5) == "VRAM:" then
        local addr = tonumber(line:sub(6))
        local val = ppu.readbyte(addr)
        client:send(string.char(val))

    elseif line:sub(1, 7) == "PIXELS:" then
        local coords = {}
        for value in string.gmatch(line:sub(8), '[^,]+') do
            table.insert(coords, tonumber(value))
        end
        local x0, y0, w, h = coords[1], coords[2], coords[3], coords[4]
        local out = {}
        for y = y0, y0 + h - 1 do
            for x = x0, x0 + w - 1 do
                local r, g, b = emu.getscreenpixel(x, y, true)
                table.insert(out, string.char(r, g, b))
            end
        end
        client:send(table.concat(out))

    elseif line:sub(1, 5) == "PADS:" then
        local mask = tonumber(line:sub(6))
        screen_log(string.format("[INPUT] Applying controller mask: bitmask 0x%02X", mask))
        
        local buttons = {
            A      = bit.band(mask, 0x01) ~= 0,
            B      = bit.band(mask, 0x02) ~= 0,
            Select = bit.band(mask, 0x04) ~= 0,
            Start  = bit.band(mask, 0x08) ~= 0,
            Up     = bit.band(mask, 0x10) ~= 0,
            Down   = bit.band(mask, 0x20) ~= 0,
            Left   = bit.band(mask, 0x40) ~= 0,
            Right  = bit.band(mask, 0x80) ~= 0
        }
        joypad.set(1, buttons)
        client:send("ACK\n")
        
    elseif line == "NMI_ENABLED" then
        local ppuctrl = memory.readbyte(0x2000)
        if bit.band(ppuctrl, 0x80) ~= 0 then
            client:send("1\n")
        else
            client:send("0\n")
        end
    end
end
