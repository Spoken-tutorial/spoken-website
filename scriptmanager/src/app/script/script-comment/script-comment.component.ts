import { Component, OnInit, Input, Output, EventEmitter } from '@angular/core';
import * as $ from 'jquery';

@Component({
  selector: 'app-script-comment',
  templateUrl: './script-comment.component.html',
  styleUrls: ['./script-comment.component.sass']
})
export class ScriptCommentComponent implements OnInit {
  @Input() newComment: string = "";
  @Input() comments: any;
  @Output() commentEmitter = new EventEmitter<string>();
  comment_value = "";

  constructor() { }

  public addComment() {
    if (this.newComment.trim() != "") {
      this.commentEmitter.emit(this.newComment);
      this.newComment = "";
      this.comment_value = "";
    }
  }

  commentKey(event) { this.newComment = event.target.value; }

  ngOnInit() {
    var element = document.getElementById("fixedComments");
    element.scrollTop = element.scrollHeight;
  }

}