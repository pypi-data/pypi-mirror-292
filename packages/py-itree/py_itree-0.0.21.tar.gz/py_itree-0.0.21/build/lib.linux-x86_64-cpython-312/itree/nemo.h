#pragma once
#include "common.h"
#include "shared.h"

std::string compress_string(const std::string &str, int compressionlevel);

std::string decompress_string(const std::string &str);

string encode(string s);

string decode(const py::str &);
