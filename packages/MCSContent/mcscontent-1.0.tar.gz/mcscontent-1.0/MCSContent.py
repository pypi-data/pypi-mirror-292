def main():
    print("本程序由Ray开发")
    print("Copyright Ray 2024")
if __name__ == "__main__":
    main()
def vscontent(ct):
    vs=str(ct)
    startevspos=vs.rfind("VersionDict(name_raw=")
    startvspos=int(startevspos)+22
    endevspos=vs.index(", name_clean")
    endvspos=int(endevspos)-1
    version=vs[startvspos:endvspos]
    return version
def mdcontent(ct):
    md=str(ct)
    startemdpos=md.rfind("MOTDDict(raw=")
    startmdpos=int(startemdpos)+14
    endemdpos=md.index(", clean=")
    endmdpos=int(endemdpos)-1
    motd=md[startmdpos:endmdpos]
    return motd
