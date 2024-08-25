#include "pickle.h"

namespace py = pybind11;
using namespace std;
using namespace pybind11::literals;

py::str run_length_dict(const py::dict &d) {
    if (d.empty())
        return py::str("0#", 2);
    auto extra_ = d.cast<py::str>();
    extra_ = "{}#{}"_s.format(py::len(extra_), extra_);
    return extra_;
}

py::dict to_dict(const string &s) {
    if (s.empty()) {
        return py::dict();
    }
    auto ast = py::module::import("ast");
    try {
        return ast.attr("literal_eval")(s);
    } catch (const std::exception &e) {
        cout << "warning: " << s << ", error: " << e.what() << endl;
        return py::dict();
    }
}

py::dict str_to_dict(const string &dict_str) {
    if (dict_str == "0#")
        return py::dict();
    auto vs = split(dict_str, "#", 1);
    if (vs.size() <= 1) {
        return py::dict();
    }
    return to_dict(vs[1]);
}

py::str serialize_node_(const shared_ptr<Node> &n) {
    py::str s("n1*", 3);
    return serialize_node_impl(n, s);
}

py::str serialize_node_impl(const shared_ptr<Node> &n, py::str &s) {
    if (n != nullptr) {
        py::str extra_ = run_length_dict(n->extra);
        auto tmp = "{},{},{},{}${}"_s.format(n->name, n->start, n->end, n->nid, extra_);
        // py::print(tmp);
        // s += py::str("{", 1) + tmp;
        s = "{}[{}"_s.format(s, tmp);
        // py::print(123);
        // py::print(s);
        for (auto i = n->nodes.begin(); i != n->nodes.end(); i++)
            s = serialize_node_impl(*i, s);
        // s += py::str("]", 1);
        s = "{}]"_s.format(s);
    }
    // py::print(s);
    return s;
}

py::str serialize_tree_(const shared_ptr<Tree> &n) {
    auto run_length_extra = run_length_dict(n->extra);
    // py::str s = "t1^{tid},{pid},{mode},{count},{depth},{monotonic},{zin_threshold},{run_length_extra}"_s.format(
    py::str s = "t1^{},{},{},{},{},{},{},{}"_s.format(
        n->tid, n->pid, n->mode, n->count, n->depth, int(n->monotonic), n->zin_threshold, run_length_extra);
    py::str ns = serialize_node_(n->root);
    return "{}%{}"_s.format(s, ns);
}

shared_ptr<Node> deserialize_node_(py::str bs) {
    string d = static_cast<std::string>(bs);
    auto i = d.find("*");
    if (i == string::npos) {
        // cout << d << endl;
        throw invalid_argument(d);
    }
    string version_str = d.substr(1, i - 1);
    // py::print("version_strxxxxxxxxxxx:", version_str);
    int version = stoi(version_str);
    assert(version == 1);
    // py::print("--------------------------------");
    // py::print("version:", version);
    return deserialize_node_impl(d.substr(i + 1));
}

shared_ptr<Node> deserialize_node_impl(const string &d) {
    vector<shared_ptr<Node>> stk_ = {create_virtual_node_()};
    string s;
    size_t i = 0;
    // cout << "d:" << d << endl;
    while (i < d.size()) {
        // py::print(py::str(to_string(i)));
        auto ch = d[i];
        if (ch == '[') {
            if (stk_.size() == 1) {
                stk_.push_back(create_tmp_node());
                stk_[0]->append(stk_[1]);
            } else {
                auto t = create_tmp_node();
                stk_.back()->append(t);
                stk_.push_back(t);
            }
        } else if (ch == '$') {
            vector<string> kv = split(s, ",");
            // py::print("kv:", kv[0], kv[1], kv[2], kv[3]);
            stk_.back()->name = kv[0];
            stk_.back()->start = stod(kv[1]);
            stk_.back()->end = stod(kv[2]);
            stk_.back()->nid = stoi(kv[3]);
            s = "";
            string tmp = d.substr(i + 1);
            // cout << "i+1:" << i + 1 << endl;
            // cout << "tmp:" << tmp << endl;
            auto vs = split(tmp, "#", 1);
            // cout << "tmp:" << vs.size() << endl;
            string extra_len_str = vs[0], remaining = vs[1];
            // py::print("extra_len_str", py::str(extra_len_str));
            int extra_len = stoi(extra_len_str);
            if (extra_len > 0) {
                string dict_str = remaining.substr(0, extra_len);
                // py::print(py::str(dict_str));
                stk_.back()->extra = to_dict(dict_str);
            }
            i += extra_len + 1 + extra_len_str.size() + 1;
            continue;
        } else if (ch == ']') {
            if (stk_.size() > 1) {
                stk_.pop_back();
            }
        } else {
            s.push_back(ch);
        }
        i++;
    }
    // py::print("vvvvvvvvvvvvvv");
    // auto r = consolidate(stk_.front());
    // py::print(stk_.front()->nodes.front());
    return stk_.front()->nodes.front();
}

shared_ptr<Tree> deserialize_tree_(py::str bs) {
    string d = static_cast<std::string>(bs);
    auto tree = create_tmp_tree();
    if (d.empty())
        return tree;
    if (d[0] != 't') {
        throw invalid_argument(d);
    }
    auto v = split(d, ",", 7);
    auto v1 = split(v[0], "^");
    int version = stoi(v1[0].substr(1));
    assert(version == 1);

    tree->tid = v1[1];
    tree->pid = v[1];
    tree->mode = stoi(v[2]);
    tree->count = stoi(v[3]);
    tree->depth = stoi(v[4]);
    tree->monotonic = stoi(v[5]);
    tree->zin_threshold = stod(v[6]);
    string &t = v[7];
    auto v2 = split(t, "#", 1);
    int run_len = stoi(v2[0]);
    auto dict_ = v2[1].substr(0, run_len);
    tree->extra = to_dict(dict_);
    auto rest = v2[1].substr(run_len + 1);
    assert(v2[1][run_len] == '%');

    shared_ptr<Node> root = deserialize_node_(rest);
    tree->root = root;
    return tree;
}

void _deserialize_tree(Tree *tree, py::str bs) {
    string d = static_cast<std::string>(bs);
    if (d.empty())
        return;
    if (d[0] != 't') {
        throw invalid_argument(d);
    }
    auto v = split(d, ",", 7);
    auto v1 = split(v[0], "^");
    int version = stoi(v1[0].substr(1));
    assert(version == 1);

    tree->tid = v1[1];
    tree->pid = v[1];
    tree->mode = stoi(v[2]);
    tree->count = stoi(v[3]);
    tree->depth = stoi(v[4]);
    tree->monotonic = stoi(v[5]);
    tree->zin_threshold = stod(v[6]);
    string &t = v[7];
    auto v2 = split(t, "#", 1);
    int run_len = stoi(v2[0]);
    auto dict_ = v2[1].substr(0, run_len);
    tree->extra = to_dict(dict_);
    auto rest = v2[1].substr(run_len + 1);
    assert(v2[1][run_len] == '%');

    shared_ptr<Node> root = deserialize_node_(rest);
    tree->root = root;
}

py::str serialize_forest_(const ForestStats &fr) {
    py::str s = "f1^{}🆃{}🆃{}🆃{}🆃{}🆃{}🆃{}🆃{}🆃{}🆃{}🆃{}🆃{}"_s.format(fr.init_time_us,
                                                                  fr.dio_bytes_r,
                                                                  fr.dio_bytes_w,
                                                                  fr.sio_bytes_r,
                                                                  fr.sio_bytes_w,
                                                                  fr.nio_bytes_r,
                                                                  fr.nio_bytes_w,
                                                                  fr.overhead_us,
                                                                  int(fr.enabled),
                                                                  int(fr.attach_timestamp),
                                                                  fr.itree_tpl,
                                                                  int(fr.fast_fail));
    return s;
}

ForestStats deserialize_forest_(const py::str &bs) {
    auto fr = ForestStats();
    // py::print(bs);
    string d = static_cast<std::string>(bs);
    auto v1 = split(d, "^", 1);
    auto v2 = split(v1[1], "🆃");
    // py::print("v2:", v2[0], v2[1], v2[2], v2[3], v2[4], v2[5], v2[6], v2[7], v2[8], v2[9], v2[10], v2[11]);
    fr.init_time_us = stoll(v2[0]);
    fr.dio_bytes_r = stoll(v2[1]);
    fr.dio_bytes_w = stoll(v2[2]);
    fr.sio_bytes_r = stoll(v2[3]);
    fr.sio_bytes_w = stoll(v2[4]);
    fr.nio_bytes_r = stoll(v2[5]);
    fr.nio_bytes_w = stoll(v2[6]);
    fr.overhead_us = stoll(v2[7]);
    fr.enabled = stoi(v2[8]);
    fr.attach_timestamp = stoi(v2[9]);
    fr.itree_tpl = v2[10];
    fr.fast_fail = stoi(v2[11]);
    return fr;
}
