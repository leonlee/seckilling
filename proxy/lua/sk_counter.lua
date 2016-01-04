local _M = {}
local config = require "config"

function _M.incr()
    local cache = ngx.shared.scache
    local val, err = cache:incr("counter", 1)
    if not val then
        ngx.log(ngx.ERR, "can't get counter", err)
    end

    return val, err
end

function _M.apply() 
    local cache = ngx.shared.scache
    local val, err = cache:get("counter")
    if not val then
        ngx.log(ngx.ERR, "can't get counter", err)
    end

    if val >= config.counterBatch then
        local redisc = require "redisc"
        local redis = redisc:new()

        local maxCount, err = redis:get("max_count")
        if not maxCount then
            maxCount = config.maxCount
            ngx.log(ngx.CRIT, "can't get max_count", err)
        end
        maxCount = tonumber(maxCount)

        local count, err = redis:incrby("counter", config.counterBatch)
        if not count then
            ngx.log(ngx.CRIT, "can't incrby redis", err)
        end
        ngx.log(ngx.INFO, "redis counter ", count, " maxCount ", maxCount)

        if count >= maxCount then
            local success, err, forcible = cache:set("stopped", 1)
            if not success then
                ngx.log(ngx.ERR, "can't set stopped", err)
            end
        end
        _M.reset()
    end
end

function _M.stopped()
    local cache = ngx.shared.scache
    local val, err = cache:get("stopped")
    if not val then
        ngx.log(ngx.CRIT, "can't get stopped", err)
    end

    return val == 1
end

function _M.enable()
    local cache = ngx.shared.scache

    local success, err, forcible = cache:set("stopped", 0)
    if not success then
        ngx.log(ngx.ERR, "can't clear stopped", err)
    end
end

function _M.reset()
    local cache = ngx.shared.scache
    local success, err, forcible = cache:set("counter", 0)
    if not success then
        ngx.log(ngx.ERR, "can't reset counter", err)
    end
end

function _M.get()
    local cache = ngx.shared.scache
    local val, flags =  cache:get("counter")
    return val
end

return _M
