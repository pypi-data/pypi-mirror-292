import importlib
import pkgutil
from pyco_types._common import G_Symbol_UNSET

_g_import_cached = {}


def gen_attr_of_package(
    attr_name, package=None, nullable=False,
    include_mod_names=None, exclude_mod_names=None,
    only_pkg=False, max_depth=3, **kwargs
):
    """
    @yield: (val, modname, module, int(ispkg))
    ; set _g_import_cached[(pkg_name, attr_name)] = @yield
    ; set _g_import_cached[(modname, attr_name)] = @yield 
    
     
    """
    global _g_import_cached
    cnt_res = 0
    pkg_name = getattr(package, "__name__", "")
    if isinstance(include_mod_names, list):
        for modname in include_mod_names:
            try:
                module = importlib.import_module(modname)
                if hasattr(module, attr_name):
                    val = getattr(module, attr_name)
                    res = (val, modname, module, 2)
                    _g_import_cached[(pkg_name, attr_name)] = res
                    _g_import_cached[(modname, attr_name)] = res 
                    cnt_res += 1
                    yield val, modname, module, 2
            except Exception as e:
                continue
    else:
        for importer, modname, ispkg in pkgutil.walk_packages(
            package.__path__, pkg_name + '.'
        ):
            if isinstance(exclude_mod_names, list):
                if modname in exclude_mod_names:
                    continue
            else:
                if only_pkg and not ispkg:
                    continue
                if max_depth > 0 and len(modname.split(".")) > max_depth:
                    continue

            try:
                module = importlib.import_module(modname)
                if hasattr(module, attr_name):
                    val = getattr(module, attr_name)
                    res = (val, modname, module, int(ispkg)) 
                    _g_import_cached[(pkg_name, attr_name)] = res
                    _g_import_cached[(modname, attr_name)] = res 
                    cnt_res += 1
                    yield val, modname, module, int(ispkg)

            except ImportError:
                continue
    if cnt_res == 0:
        if not nullable:
            raise ImportError(
                f"failed to find {pkg_name}[@attr={attr_name}]"
                f"("
                f"\n\tinclude_mod_names={include_mod_names},"
                f"\n\texclude_mod_names={exclude_mod_names},"
                f"\n\tonly_pkg:{only_pkg},max_depth:{max_depth}, "
                f")"
            )
        yield None


def get_attr_of_package(attr_name, package, force_retry=False, **kwargs):
    global _g_import_cached
    pkg_name = getattr(package, "__name__", "")
    pkey = (pkg_name, attr_name)
    pres = _g_import_cached.get(pkey, G_Symbol_UNSET)
    if pres is None and not force_retry:
        raise ImportError(f"failed to find {pkg_name}[@attr={attr_name}], retry by set `force_retry=True`")
    elif pres is not G_Symbol_UNSET:
        return pres[0]
        
    for pres in gen_attr_of_package(attr_name, package, nullable=True, **kwargs):
        _g_import_cached[pkey] = pres
        if pres is not None:
            return pres[0]
        else:
            raise ImportError(f"failed to find {pkg_name}[@attr={attr_name}]")

