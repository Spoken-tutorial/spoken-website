import { Component, OnInit, Input, Output, EventEmitter } from '@angular/core';

@Component({
  selector: 'app-script-comment-box',
  templateUrl: './script-comment-box.component.html',
  styleUrls: ['./script-comment-box.component.sass']
})
export class ScriptCommentBoxComponent implements OnInit {
  @Input() comment: any;
  @Input() index: number;
  @Output() saveCommentEmitter = new EventEmitter<number>();

  isEditable: boolean = false;

  constructor() { }

  makeEditable() {
    this.isEditable = true;
  }

  saveComment() {
    this.saveCommentEmitter.emit(this.index);
    this.isEditable = false;
  }

  ngOnInit() {
  }

}
