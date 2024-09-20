local protocol_fiubardt = Proto("fiubardt", "RDT FIUBA")


local syn = ProtoField.uint8("fiubardt.syn", "SYN")
local ack = ProtoField.uint8("fiubardt.ack", "ACK")
local action = ProtoField.uint8("fiubardt.action", "ACTION")
local protocol = ProtoField.uint8("fiubardt.protocol", "PROTOCOL")
local fin = ProtoField.uint8("fiubardt.fin", "FIN")
local error = ProtoField.uint8("fiubardt.error","Error")
local seq_number = ProtoField.uint32("fiubardt.sequence_number", "SEQ NUMBER")
local length = ProtoField.uint16("fiubardt.length", "Length")
local data = ProtoField.bytes("fiubardt.data", "Data")


protocol_fiubardt.fields = {syn, ack, action, protocol, fin,error, seq_number, length, data}

function protocol_fiubardt.dissector(buf, pinfo, tree)
    local subtree = tree:add(protocol_fiubardt, buf())

    subtree:add(syn, buf(0, 1))
    subtree:add(ack, buf(1, 1))
    subtree:add(action, buf(2, 1))
    subtree:add(protocol, buf(3, 1))
    subtree:add(fin, buf(4, 1))
    subtree:add(error,buf(5,1))
    local seq_number_value = buf:range(6, 4):le_uint()
    subtree:add(seq_number, seq_number_value)
    local length_value = buf:range(10, 2):le_uint()
    subtree:add(length, length_value)
    subtree:add(data, buf(12))
    -- subtree:add(length, buf(10, 4))
    -- subtree:add(data, buf(13))

    pinfo.cols.protocol:set("RDT FIUBA")
end


local udp_port = DissectorTable.get("udp.port")
udp_port:add(8080, protocol_fiubardt)
