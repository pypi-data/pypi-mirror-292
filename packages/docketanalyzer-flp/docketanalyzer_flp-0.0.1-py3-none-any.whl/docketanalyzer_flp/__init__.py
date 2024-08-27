modules = {
    'docketanalyzer_flp.juri': ['JuriscraperUtility'],
}


from docketanalyzer import lazy_load_modules
lazy_load_modules(modules, globals())
