import { Component, OnInit, Input, Output, EventEmitter } from '@angular/core';

@Component({
  selector: 'app-script-comment',
  templateUrl: './script-comment.component.html',
  styleUrls: ['./script-comment.component.sass']
})
export class ScriptCommentComponent implements OnInit {
  @Input() newComment: string = '';
  @Input() comments: any;
  @Output() commentEmitter = new EventEmitter<string>();

  constructor() { }

  public addComment() {
    if (this.newComment.trim() != '') {
      this.commentEmitter.emit(this.newComment);
      this.newComment = '';
    }
  }

  public clearTextarea(event) {
    event.target.value = '';
  }

  commentKey(event) { this.newComment = event.target.value; }

  ngOnInit() {

  }

}