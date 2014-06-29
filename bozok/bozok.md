# Bozok

## General

Bozok is a RAT written in Delphi. This is just some info regarding its configuration.

## Finding the version

In the config loading function, Bozok first sets the version string, then tries to load a `RT_RCDATA` resource called `"CFG"`.
Since these strings (`"CFG"` and the version string) are hard coded and follow each other, they can be found adjacent in the code segment:

    00402698  5A C3 00 00 43 46 47 00  31 00 2E 00 30 00 00 00  Z+..CFG.1...0...
  
Thus the version can be found by searching for the string `"CFG"` followed by a (unicode) version string:

    b'CFG\x00((?:[0-9]\x00(?:\.\x00)?)+)\x00\00'

Of 382 Bozok samples I found the following version distribution:

    {
      "1.0a": 26,
      "1.0b": 76,
      "1.1": 52,
      "1.2": 5,
      "1.2.1": 3,
      "1.3": 51,
      "1.3.1": 23,
      "1.4": 10,
      "1.4.1": 17,
      "1.4.3": 55,
      "1.5": 61,
      "1.5.1": 40
    }
  
## The config data

All versions (I have looked at) saves the config in a `RT_RCDATA` resource entry called `"CFG"`, and loads it 
with `FindResource`/`LoadResource`/`LockResource`.

If it can't find the resource, some hard coded default values are used:
  
    // Bozok 1.0a
    flag_exe = 0;
    flag_reg = 1;
    ips = (int)"localhost";
    server_id = (int)L"TEST_ID";
    exe_name = (int)L"msserv.exe";
    reg_name = (int)L"Microsoft Server";
    v1 = (int)L"MUTX_BOZOK";
    mutex_name = (int)L"MUTX_BOZOK";
    port = 80;
    
    // Bozok 1.5.1
    flag_exe = 0;
    flag_reg = 0;
    flag_visible = 1;
    flag_unknown1 = 0;
    flag_unknown2 = 0;
    flag_unknown3 = 0;
    ips = (int)"localhost";
    server_id = (int)L"TEST_ID";
    exe_name = (int)L"prjBozok.exe";
    reg_name = (int)L"Microsoft Server";
    mutex_name = (int)L"MUTEX_BOZOK";
    password = (int)L"mypass";
    result = (int)L"plug.dat";
    extension_name = (int)L"plug.dat";
    port = 1515;

These varies in the samples I have looked at.
  
The format of the config data has changed with versions and are described below.

### Bozok 1.0 

I found two "groups" of 1.0 samples that I dubbed 1.0a and 1.0b. 
The 1.0b version have added support for password protection, so the config data
differs a little bit from the 1.0a versions.

Both versions saves the config as a fixed size struct:

    cfg_1_0_a {
      char ips[255];
      char exe[100];
      char reg[100];
      char id[100];
      char mutex[100];
      int port;
      char flag_exe;
      char flag_reg;
    }

    cfg_1_0_b {
      char ips[255];
      char exe[100];
      char reg[100];
      char id[100];
      char mutex[100];
      char pass[100];       // not present in 1.0a
      int port;
      char flag_exe;
      char flag_reg;
    }
    
### Bozok 1.1 and above

From version 1.1 the config is saved as a unicode string, and the different fields of the config is separated by a pipe (`|`):

    ; .rsrc 
    0040C120  54 00 65 00 73 00 74 00  53 00 65 00 72 00 76 00  T.e.s.t.S.e.r.v.
    0040C130  65 00 72 00 7C 00 53 00  73 00 4E 00 58 00 50 00  e.r.|.S.s.N.X.P.
    0040C140  32 00 61 00 66 00 31 00  57 00 47 00 4A 00 6F 00  2.a.f.1.W.G.J.o.
    0040C150  7C 00 73 00 65 00 72 00  76 00 65 00 72 00 2E 00  |.s.e.r.v.e.r...
    0040C160  65 00 78 00 65 00 7C 00  6D 00 20 00 6D 00 7C 00  e.x.e.|.m. .m.|.
    0040C170  65 00 78 00 74 00 2E 00  64 00 61 00 74 00 7C 00  e.x.t...d.a.t.|.
    0040C180  6D 00 79 00 70 00 61 00  73 00 73 00 7C 00 31 00  m.y.p.a.s.s.|.1.
    0040C190  7C 00 31 00 7C 00 31 00  7C 00 30 00 7C 00 30 00  |.1.|.1.|.0.|.0.
    0040C1A0  7C 00 31 00 35 00 31 00  35 00 7C 00 31 00 32 00  |.1.5.1.5.|.1.2.
    0040C1B0  37 00 2E 00 30 00 2E 00  30 00 2E 00 31 00 2A 00  7...0...0...1.*.
    0040C1C0  7C 00 30 00 7C 00 00 00  20 23 20 61 71 73 00 6D  |.0.|... # aqs.m

The form is:

    server_id|mutex_name|exe_name|reg_key|ext_name|password|flags|port|ips
  
The IPs (or domains) are separated by an asterisk (`*`):

    syskiller29dz.no-ip.biz*mascara29sys.no-ip.info*
  
The flags are five values either being `"1"` or `"0"`:
  
    install_exe|install_reg|visible_mode|unknown_flag1|unknown_flag2
  
The two last flags does not seem to be used in the code (yet).

Later versions (> 1.3) also have one or more flags after the `ips` field. It doesn't seem like they are being used either.

    server_id|mutex_name|exe_name|reg_key|ext_name|password|flags|port|ips|flags
