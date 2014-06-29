rule Bozok : RAT
{
  strings:
    $ = { 43 46 47 00 31 00 2E 00 [2-6] 00 00 }               // "CFG" u"1"
    $ = "%s|%s|%s|%s|%d|%s|%d|%d" wide

   condition:
    all of them
}

