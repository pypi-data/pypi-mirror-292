function startswith(s, prefix)
  return s:sub(1, #prefix) == prefix
end

function split(s, separator)
  local t = {}
  for found in string.gmatch(s, "([^" .. separator .. "]+)") do
    t[#t + 1] = found
  end
  return t
end

local path = request_handle:headers():get(":path")

local resemble_prefix = "/__/resemble/"

if startswith(path, resemble_prefix) then
  local values = split(path, "/")

  local service_name = values[3]
  if service_name == nil then
    request_handle:respond(
      {[":status"] = "400"},
      "ERROR: Missing 'service_name' path parameter")
  end
  local state_ref = values[4]
  if state_ref == nil then
    request_handle:respond(
      {[":status"] = "400"},
      "ERROR: Missing 'state_ref' path parameter")
  end

  request_handle:headers():replace("x-resemble-service-name", service_name)
  request_handle:headers():replace("x-resemble-state-ref", state_ref)

  request_handle:headers():replace(":path", "/" .. table.concat({ table.unpack(values, 5) }, "/"))
end
