let
  nixpkgs = fetchTarball "https://github.com/NixOS/nixpkgs/tarball/nixos-22.11";
  pkgs = import nixpkgs { config = {}; overlays = []; };
in
{
  ffmpeg = pkgs.callPackage ./ffmpeg.nix { };
  libaom = pkgs.callPackage ./codecs/libaom.nix { };
  ffbasic = pkgs.callPackage ./ffbasic.nix { };
}