import { Component, OnInit, Input, Output, EventEmitter } from '@angular/core';

@Component({
  selector: 'app-script-revision',
  templateUrl: './script-revision.component.html',
  styleUrls: ['./script-revision.component.sass']
})
export class ScriptRevisionComponent implements OnInit {
  // public revisions:any = [];
  @Input() revisions: any;
  @Output() revisionEmitter = new EventEmitter<number>();

  constructor() { }

  public showRevisionModal(index) {
    // console.log(index)
    this.revisionEmitter.emit(index);
  }

  ngOnInit() {
    // this.getRevisions()
  }

}
