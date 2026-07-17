# OSS計測器接続管理調査記録

分類: `OBSERVED / INFERRED / PLANNED`  
日付: 2026-07-17

## OBSERVED

- lxi-guiは手動追加GUIにName、IP、VXI11/RAW、portを持つ。
- 手動登録はrandom UUID付きJSONとしてGSettingsへ永続化される。
- lxi-toolsはVXI-11/mDNS discoveryを持ち、tested listにSDS1204X-Eを掲載する。
- lxi-guiの登録schemaにはmemo、MAC、serial、firmware、sighting history、pairing stateがない。
- ngscopeclientはnickname、recent connection、YAML session、Lab Notes、offline openを持つが、online openは
  保存済み設定を実機へ再適用し得る。
- OpenTAP、QCoDeS、PyVISA、sigrokは部分機能を持つが、PSYCHOのpairing要件全体とは一致しない。

## INFERRED

- lxi-guiのUXとliblxi discoveryは再利用価値が高い。
- pairing正本をlxi-gui GSettingsへ委ねると、identity履歴と権限分離が不足する。
- PSYCHO固有SQLiteは過剰な再発明ではなく、発見と本人確認と実機権限を分けるための薄い差分になる。

## PLANNED

- nickname、IP/hostname、任意memoを`DRAFT`としてnetwork I/Oなしで保存するGUIを設計する。
- 別のquery-only Link後にvendor/model/serial/firmwareと任意MAC observationを保存する。
- liblxiは直接linkまたは固定CLI adapterの双方を比較し、license/borrow ledgerを残す。
- Linkから測定開始、設定変更、波形取得へ自動昇格させない。

## Claim Boundary

候補OSSをinstall、build、実機試験していない。lxi-toolsのSDS1204X-E動作はupstream tested listの主張であり、
この環境での再現事実ではない。完全一致OSSが世界に存在しないとは断定しない。

## Inner Memo

lxi-guiは玄関と住所録をすでに作っていた。PSYCHOが新しく作るべきものは玄関そのものではなく、
呼び鈴を押した記録、名札の原本、引っ越し履歴、そして住所録のボタンが勝手に測定開始へ化けない境界だ。
