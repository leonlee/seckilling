package model

import (
	"errors"
)

const (
	CookieCheckFailed = 210

	UserPhoneNumNull  = 250
	PhoneRepaet       = 256
	InvalidStatus     = 266
	StatusNull        = 267
	EventNull         = 268
	EventNotMatch     = 269
	GetStatusFailed   = 281
	GetPhoneNumFailed = 282
	GetEventFailed    = 283
	GetCtEventFailed  = 284

	ShortageStock = 290

	RedisError = 295

	UnknownError = 299
)

var (
	ShortageStockError = errors.New("award have sold out")
)
