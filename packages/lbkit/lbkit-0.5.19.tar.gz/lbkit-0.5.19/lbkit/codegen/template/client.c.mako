#include "gcl_base.h"
#include "${intf.name}.h"

<% class_name = intf.alias + "_Cli"
properties = "_" + class_name + "_properties"
signal_processer = "_" + class_name + "_signals"
method_processer = "_" + class_name + "_methods"
%>\
static const ${intf.alias}_Methods *${method_processer} = NULL;
static ${intf.alias}_Properties ${properties};
static const ${intf.alias}_Signals *${signal_processer} = NULL;

% for prop in intf.properties:
## 私有属性或者只读属性
% if not prop.private and prop.access != "read":
    % if prop.deprecated:
__attribute__((__deprecated__)) gint ${class_name}_set_${prop.name}(const ${class_name} *object,
    ${", ".join(prop.declare()).replace("<arg_name>", prop.name).replace("<const>", "const ")}, GError **error)
    % else:
gint ${class_name}_set_${prop.name}(const ${class_name} *object,
    ${", ".join(prop.declare()).replace("<arg_name>", prop.name).replace("<const>", "const ")}, GError **error)
    % endif
{
    cleanup_unref GVariant *tmp = NULL;
    % for line in prop.encode_func():
    ${line.replace("<arg_out>", "tmp").replace("n_<arg_name>", "n_" + prop.name).replace("<arg_name>", prop.name)};
    % endfor
    return gcl_impl.write_property((GclObject *)object, &${properties}.${prop.name}, tmp, error);
}

% endif
## 私有或只写属性不允许读
% if not prop.private and prop.access != "write":
    % if prop.deprecated:
__attribute__((__deprecated__)) gint ${class_name}_get_${prop.name}(const ${class_name} *object,
    ${", ".join(prop.out_declare()).replace("<arg_name>", "value").replace("<const>", "")}, GError **error)
    % else:
gint ${class_name}_get_${prop.name}(const ${class_name} *object, ${", ".join(prop.out_declare()).replace("<arg_name>", "value").replace("<const>", "")}, GError **error)
    % endif
{
    % if "gsize n_" in prop.declare()[0]:
    g_assert(n_value && value);
    % else:
    g_assert(value);
    % endif
    % for line in prop.declare():
        % if "*" in line:
    ${line.strip().replace("<arg_name>", "tmp_value").replace("<const>", "")} = NULL;
        % else:
    ${line.strip().replace("<arg_name>", "tmp_value").replace("<const>", "")};
        % endif
    % endfor
    GVariant *out = NULL;

    gint ret = gcl_impl.read_property((GclObject *)object, &${properties}.${prop.name}, &out, error);
    if (ret == 0 && out) {
    % for line in prop.decode_func():
        ${line.replace("<arg_in>", "tmp_value").replace("<arg_name>", "out")};
    % endfor
        *value = tmp_value;
    % if "gsize n_" in prop.declare()[0]:
        *n_value = n_tmp_value;
    % endif
    }
    if (out) {
        g_variant_unref(out);
    }
    return ret;
}

% endif
% endfor

% for method in intf.methods:
<% RSP_PARA = f'' %>\
<% REQ_PARA = f'' %>\
    % if len(method.returns.parameters) > 0:
<% RSP_PARA = f'{intf.alias}_{method.name}_Rsp **rsp, ' %>\
    % endif
    % if len(method.parameters.parameters) > 0:
<% REQ_PARA = f'const {intf.alias}_{method.name}_Req *req, ' %>\
    % endif
int ${class_name}_Call_${method.name}(const ${class_name} *object,
    ${REQ_PARA}${RSP_PARA}gint timeout,
    GError **error)
{
    if (error == NULL) {
        log_error("Emit method ${method.name} with parameter error, error is NULL");
        return -1;
    }
    if (object == NULL) {
        *error = g_error_new(G_DBUS_ERROR, G_DBUS_ERROR_FAILED, "Call method ${method.name} with parameter error, object is NULL");
        return -1;
    }
    % if len(method.returns.parameters) == 0:
    void **rsp = NULL;
    % endif
    % if len(method.parameters.parameters) == 0:
    void *req = NULL;
    % endif
    return gcl_impl.call_method((GclObject *)object, (const GclMethod *)&${method_processer}->${method.name},
                                 (void *)req, (void **)rsp, timeout, error);
}

% endfor
static GclObject *_${class_name}_create(const gchar *obj_name, gpointer opaque);

static GclInterface _${class_name}_interface = {
    .create = _${class_name}_create,
    .is_remote = 1,
    .name = "${intf.name}",
    .properties = (GclProperty *)&${properties},
    .interface = NULL, /* load from usr/share/dbus-1/interfaces/${intf.name}.xml by gcl_init */
};

/**
 * @brief 分配对象
 *
 * @param obj_name 对象名，需要由调用者分配内存
 * @param opaque 上层应用需要写入对象的用户数据，由上层应用使用
 */
GclObject *_${class_name}_create(const gchar *obj_name, gpointer opaque)
{
    ${class_name} *obj = g_new0(${class_name}, 1);
    memcpy(obj->_base.magic, GCL_MAGIC, strlen(GCL_MAGIC) + 1);
    obj->_base.lock = g_new0(GRecMutex, 1);
    g_rec_mutex_init(obj->_base.lock);
    obj->_base.name = obj_name;
    obj->_base.intf = &_${class_name}_interface;
    obj->_base.opaque = opaque;
    return (GclObject *)obj;
}

% for signal in intf.signals:
% if signal.deprecated:
__attribute__((__deprecated__)) guint ${class_name}_Subscribe_${signal.name}(${class_name}_${signal.name}_Signal handler,
    const gchar *bus_name, const gchar *object_path, const gchar *arg0, gpointer user_data)
% else:
guint ${class_name}_Subscribe_${signal.name}(${class_name}_${signal.name}_Signal handler,
    const gchar *bus_name, const gchar *object_path, const gchar *arg0, gpointer user_data)
% endif
{
    return gcl_impl.subscribe_signal(&_${class_name}_interface, bus_name,
        (const GclSignal *)&${signal_processer}->${signal.name},
        object_path, arg0, (gcl_signal_handler)handler, user_data);
}

% if signal.deprecated:
__attribute__((__deprecated__)) void ${class_name}_Unsubscribe_${signal.name}(guint *id)
% else:
void ${class_name}_Unsubscribe_${signal.name}(guint *id)
% endif
{
    return gcl_impl.unsubscribe_signal(id);
}

% endfor
GclInterface *${class_name}_interface(void)
{
    return &_${class_name}_interface;
}

${class_name}_Properties *${class_name}_properties(void)
{
    return &${properties};
}

static void __attribute__((constructor(150))) ${class_name}_register(void)
{
    // 从公共库中复制信号处理函数
    ${signal_processer} = ${intf.alias}_signals();

    // 从公共库中复制方法处理函数
    _${class_name}_interface.methods = (GclMethod *)${intf.alias}_methods();
    _${class_name}_interface.signals = (GclSignal *)${intf.alias}_signals();
    ${method_processer} = ${intf.alias}_methods();

    // 从公共库中复制属性信息
    memcpy(&${properties}, ${intf.alias}_properties_const(), sizeof(${properties}));
    gcl_interface_register(&_${class_name}_interface,
                           "${intf.introspect_xml_sha256}",
                           "/usr/share/dbus-1/interfaces/${intf.name}.xml");
}
