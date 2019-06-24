import { Component, OnInit } from '@angular/core';

@Component({
  selector: 'app-script-revision',
  templateUrl: './script-revision.component.html',
  styleUrls: ['./script-revision.component.sass']
})
export class ScriptRevisionComponent implements OnInit {
  public revisions:any = [];

  constructor() { }

  public getRevisions() {
    this.revisions = [
      {
        "id": 3,
        "cue": "fossee",
        "narration": "fosseeeeee",
        "order": "1",
        "script_id": "2",
        "date_time": "2019-06-24T05:29:46.282452Z",
        "reversion_id": 109
      },
      {
        "id": 3,
        "cue": "fossee",
        "narration": "ajhduygwe",
        "order": "1",
        "script_id": "2",
        "date_time": "2019-06-24T05:29:41.843409Z",
        "reversion_id": 108
      },
      {
        "id": 3,
        "cue": "mam",
        "narration": "ajhduygwe",
        "order": "1",
        "script_id": "2",
        "date_time": "2019-06-24T05:29:36.818361Z",
        "reversion_id": 107
      },
      {
        "id": 3,
        "cue": "mam",
        "narration": "hi",
        "order": "1",
        "script_id": "2",
        "date_time": "2019-06-24T05:29:33.521724Z",
        "reversion_id": 106
      },
      {
        "id": 3,
        "cue": "hi",
        "narration": "hi",
        "order": "1",
        "script_id": "2",
        "date_time": "2019-06-24T05:28:59.610276Z",
        "reversion_id": 105
      }
    ]
    return this.revisions
  }

  ngOnInit() {
    this.getRevisions()
  }

}
