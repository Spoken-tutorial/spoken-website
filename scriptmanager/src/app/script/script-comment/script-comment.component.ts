import { Component, OnInit, Input, Output, EventEmitter } from '@angular/core';
import * as $ from 'jquery';
import { CommentsService } from 'src/app/_service/comments.service';

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
  isEditable = false;

  constructor(
    private commentService: CommentsService
  ) { }

  public addComment() {
    if (this.newComment.trim() != "") {
      this.commentEmitter.emit(this.newComment);
      this.newComment = "";
      this.comment_value = "";
    }
  }

  commentKey(event) { this.newComment = event.target.value; }

  saveComment(index) {
    this.commentService.modifyComment(this.comments[index]['id'], this.comments[index])
      .subscribe(
        console.log,
        console.error
      );
  };

  ngOnInit() {
    var element = document.getElementById("fixedComments");
    element.scrollTop = element.scrollHeight;
  }

}